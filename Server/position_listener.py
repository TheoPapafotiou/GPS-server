import sys
sys.path.insert(0,'.')
from threading import Thread
import time
import cv2
from GPS_RPI import GPS
from Merger import Merge_Files

class PositionListener(Thread):
	"""PositionListener simulator aims to populate position variable. 
	"""
	def __init__(self):

		self.coor = None
		self.i=1
		self.j=1
		
		self.cap0 = GPS.video(0, 960, 540)
		time.sleep(2)
		self.cap2 = GPS.video(2, 960, 540)
		time.sleep(2)

		if self.cap0 is None:
			print("Error in cap0")
			self.cap0.release()
		if self.cap2 is None:
			print("Error in cap2")
			self.cap2.release()

		self.Merger = Merge_Files()
		self.GPS = GPS()
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
		countFrames = 0
		while self.__running:
            
			start = time.time()
			countFrames += 1
			_, frame0 = self.cap0.read()
			_, frame2 = self.cap2.read()

			merged_frame = self.Merger.get_merged_frame(frame0, frame2)

			self.i, self.j, self.iX, self.jX = self.GPS.tracking_procedure(merged_frame, countFrames)
			self.coor = (self.i,self.j,self.iX,self.jX)
			print("Time for GPS: ", time.time() - start)

			# Wait for 0.1 s before next adv
# 			print(20*"=")
# 			print("COUNT 10")
# 			print(20*"=")
			time.sleep(0.5)
		
		self.cap0.release()
		self.cap2.release()
			