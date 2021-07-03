import sys
sys.path.insert(0,'.')
from threading import Thread
import time
import cv2
from GPS_RPI import GPS

cap = cv2.VideoCapture(0)

class PositionListener(Thread):
	"""PositionListener simulator aims to populate position variable. 
	"""
	def __init__(self):

		self.coor = None
		self.i=1
		self.j=1
		self.countFrames=0
		
		self.cap = cv2.VideoCapture(0)

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
		Update coordinates every 0.1 seconds
		"""        
		while self.__running:
			# Generate some coordinates
			self.countFrames+=1
			_, frame = self.cap.read()
			self.i, self.j = GPS.tracking_procedure(frame, self.countFrames)
			self.coor = (complex(self.i,self.j),complex(self.i+5,self.j+5))

			# Wait for 0.1 s before next adv
			time.sleep(0.1)
			