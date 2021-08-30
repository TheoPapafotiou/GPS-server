import sys
sys.path.insert(0,'.')
from threading import Thread
import time
import cv2

class PositionListener(Thread):
    """PositionListener simulator aims to populate position variable. 
    """
    def __init__(self):

        self.coor = None
        self.X = [0.0 for i in range(5)]
        self.Y = [0.0 for i in range(5)]

        self.__running = True

        Thread.__init__(self) 

    ## Method for starting position listener simulation process.
    #  @param self          The object pointer.
    def start(self):
        self.__running = True

        super(PositionListener,self).start()

    ## Method for stopping position listener simulation process.
    #  @param self          The object pointer.
    def stop(self):
        self.__running = False
        
    ## Method for running position listener simulation process.
    #  @param self          The object pointer.
    def run(self):
        """ 
        Update coordinates every 1 seconds
        """
        countFrames = 0
        while self.__running:
            
            start = time.time()

            self.X = [0, 0, 0, 0, 0]
            self.Y = [0, 0, 0, 0, 0]
            self.coor = (self.X,self.Y)

            time.sleep(0.5)
			
