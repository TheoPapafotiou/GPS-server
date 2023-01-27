import time
import threading
from multiprocessing import Pipe
from gps_system.src.position_listener import PositionListener

class GenerateData(threading.Thread):
    """ It aims to generate coordinates for server. The object of this class simulates
    the detection of robots on the race track. Object of this class calculate the position and 
    orientation of robots, when they are executing a circle movement. It calculates the same coordinates 
    for 40 robot on the race track. So car client can subscribe on a car id number between 1 and 40. 
    """ 

    def __init__(self, markerdataset = {}):
        super(GenerateData,self).__init__()

        self._marker_dic = markerdataset

        self._streamPipe = {}
        self._readPipe = {}
        self.locker = threading.Lock()

        self.__running = True
        self.__position_listener = PositionListener()
    
    def run(self):
        """ Actualize the car client server data with the new coordinates. 
        """
        self.__position_listener.start()
        time.sleep(2)
        while self.__running:
            # waiting a period
            time.sleep(0.25)
            # calculating the position of robot
            position = self.__position_listener.coor

            with self.locker:
                for id in self._streamPipe:
                    for pipe in self._streamPipe[id]:
                        msg = {'timestamp':time.time(), 'coor':position}
                        self._streamPipe[id][pipe].send(msg) 

    def getPipe(self, id, tme):
        """Creates a pipe for the client.
        Parameters
        ----------
        id : int
            Id of car
        tme : float 
            the time of detectection
        Returns
        -------
        Pipe: pipe receiving side
        """
        with self.locker:
            if not id in self._readPipe:
                self._readPipe[id]   = {}
                self._streamPipe[id] = {}

            gpsStR, gpsStS = Pipe(duplex = False)
            self._readPipe[id][tme]   = gpsStR
            self._streamPipe[id][tme] = gpsStS

            return self._readPipe[id][tme]


    def removePipeS(self):
        """Deletes the pipe for the client.
        Parameters
        ----------
        id : int
            Id of car
        tme : float 
            the time of detectection
        """

        with self.locker:
            for markerId in self._readPipe:
                for timestamp in self._readPipe[markerId]:
                    del self._readPipe[markerId][timestamp]
                    del self._streamPipe[markerId][timestamp]

    def stop(self):
        self.removePipeS()
        self.__running = False