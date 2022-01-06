import sys
sys.path.insert(0,'.')
from threading import Thread
import time
import cv2
import socket
import json
from gps_procedure import GPS_PROC

class PositionListener(Thread):
    """PositionListener simulator aims to populate position variable. 
    """
    def __init__(self, RPI_ID, PORT, params):

        self.RPI_ID = RPI_ID
        self.coor = None
        self.i=1
        self.j=1
        
        self.cap = self.video(0, params["cap_width"], params["cap_height"])
        time.sleep(2)

        if self.cap is None:
            print("Error in cap")
            self.cap.release()

        self.GPS_PROC = GPS_PROC(params)
        self.__running = True

        # Communication parameters, create and bind socket
        self.PORT = PORT
        self.BCAST_ADDRESS = '<broadcast>'

        # Create a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.server_address = (self.BCAST_ADDRESS, self.PORT)
        
        Thread.__init__(self)

    ## Method for starting position listener simulation process.
    def start(self):
        self.__running = True

        super(PositionListener,self).start()

    ## Method for stopping position listener simulation process.
    def stop(self):
        self.__running = False
        
    ## Method for running position listener simulation process.
    def run(self):
        """ 
        Update coordinates every 1 seconds
        """
        countFrames = 0
        while self.__running:
            
            start = time.time()
            countFrames += 1
            _, frame = self.cap.read()

            self.i, self.j = self.GPS.tracking_procedure(frame, countFrames)
            
            if self.i != 0.0 or self.j != 0.0:
                self.sendCoordinates()

            print("Time for GPS: ", time.time() - start)
            time.sleep(0.1)
        
        self.cap.release()

    def video(id, width, height):
        cap = cv2.VideoCapture(id)
        cap.set(3, width)
        cap.set(4, height)

        return cap

    def sendCoordinates(self):
        
        # Send data
        value = {"RPI": self.RPI_ID, "x": self.i, "y": self.j, "timestamp": round(time.time(), 2)}
        message = json.dumps(value)
        # Debug message
        print('sending {!r}'.format(message))
        sent = self.sock.sendto(message.encode('utf-8'), self.server_address)
			
if __name__ == '__main__':
    try:
        params = {
            "track_width": 400,
            "track_height": 250,
            "ID_car": 10,
            "cap_width": 640,
            "cap_height": 480,
            "ID1": 1,
            "ID2": 2,
            "ID3": 3,
            "ID4": 4
        }
        __rpi_gps = PositionListener(0, 50001, params)
        __rpi_gps.start()
    except KeyboardInterrupt:
        # __rpi_gps.__running = False
        __rpi_gps.stop()
        __rpi_gps.join()