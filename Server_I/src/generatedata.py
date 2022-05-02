import time
import threading
from src.position_listener import PositionListener

class GenerateData(threading.Thread):
    """ It aims to generate coordinates for server. The object of this class simulates
    the detection of robots on the race track. Object of this class calculate the position and 
    orientation of robots, when they are executing a circle movement. It calculates the same coordinates 
    for 40 robot on the race track. So car client can subscribe on a car id number between 1 and 40. 
    """ 

    def __init__(self, markerdataset = {}, r = 1.0):
        super(GenerateData,self).__init__()

        self._marker_dic = markerdataset

        self.locker = threading.Lock()

        self.__running = True
        
        #: inferior value of car id number
        self.__startCarid = 1
        #: superior value of car id number
        self.__endCarid = 40

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
            pos = self.__position_listener.coor
            position = complex(pos[0], pos[1])
            # print("Sent to car:  X + jY = ", position)
            # calculation the orientation of robot.
            orientation = pos[2]
            # update the dictionary, which contains coordinates of detected robots
            for carId in range( self.__startCarid, self.__endCarid):
                with self.locker:
                    self._marker_dic[carId] = {'timestamp':time.time(), 'coor':(position, orientation)}

    def getItem(self, markerId):
        """Get timestamp and pose of markerId
        
        Parameters
        ----------
        markerId : int
            The identification number of marker.
        """
        with self.locker:
            return self._marker_dic[markerId]

    def stop(self):
        self.__running = False