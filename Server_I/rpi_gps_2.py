import sys
# sys.path.insert(0,'.')
from threading import Thread
import time
import cv2
import socket
import json
import os
import errno
from src.gps_procedure import GPS_PROC
from src.timeout       import timeout

class GPSBroadcaster(Thread):
    """PositionListener simulator aims to populate position variable. 
    """
    def __init__(self, RPI_ID, PORT, params):

        self.RPI_ID = RPI_ID
        self.coor = None
        self.params = params
        

        start = time.time()

        self.cap = self.video(params["cap_width"], params["cap_height"])

        time.sleep(2)

        if self.cap is None:
            print("Error in cap")
            self.cap.release()
            sys.exit(0)

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

        super(GPSBroadcaster,self).start()

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

            if self.params["frame_rotate"] == 1:
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

            if countFrames == 50:
                cv2.imwrite('Base_frame_' + str(self.RPI_ID), frame)
            (x, y) = self.GPS_PROC.tracking_procedure(frame, countFrames)
            
            if x != 0.0 or y != 0.0:
                self.sendCoordinates(x, y)

            # print("Time for GPS: ", time.time() - start)
            time.sleep(0.1)
        
        self.cap.release()

    @timeout(10, os.strerror(errno.ETIMEDOUT))
    def video(self, width, height):
        cap = cv2.VideoCapture(0)
        print("Cap opened!")
        cap.set(3, width)
        cap.set(4, height)
        print("Cap setup ready!")
        return cap

    def sendCoordinates(self, x, y):
        
        # Send data
        value = {"RPI": self.RPI_ID, "x": x, "y": y, "timestamp": round(time.time(), 2)}
        message = json.dumps(value)
        # Debug message
        # print('sending {!r}'.format(message))
        sent = self.sock.sendto(message.encode('utf-8'), self.server_address)
			
if __name__ == '__main__':
    try:
        params = {
            "frame_rotate": 1,
            "track_width": 190,
            "track_height": 310,
            "ID_car": 10,
            "cap_width": 640,
            "cap_height": 480,
            "Ctl": (0, 0),
            "Ctr": (405, 0),
            "Cbr": (405, 640),
            "Cbl": (0, 640)
        }
        __rpi_gps = GPSBroadcaster(2, 50003, params)
        __rpi_gps.start()
    except KeyboardInterrupt:
        # __rpi_gps.__running = False
        print("Keyboard Interrupt, cap released!")
        __rpi_gps.cap.release()
        __rpi_gps.stop()
        __rpi_gps.join()
