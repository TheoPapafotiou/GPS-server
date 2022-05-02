import sys
sys.path.insert(0,'.')
from threading import Thread
import time
import cv2
import socket
import json
import numpy as np

class PositionListener(Thread):
	"""
	PositionListener simulator aims to populate position variable. 
	"""
	def __init__(self):

		self.coor = None

		PORT1 = 50002
		PORT2 = 50003
		PORT3 = 50004

		## Distances
		distance_Arucos_height = 250

		## Offsets
		self.offX1 = 0
		self.offY1 = 0
		
		self.offX2 = 300
		self.offY2 = 45

		self.offX3 = 0
		self.offY3 = 160
		
		self.socket1 = self.init_socket(PORT1)
		self.socket2 = self.init_socket(PORT2)
		self.socket3 = self.init_socket(PORT3)

		self.start_time = round(time.time(), 2)
		self.message = []
		self.message.append((-1, 0, 0, 0, self.start_time))
		
		self.__running = True
		
		Thread.__init__(self) 

    ## Method for starting position listener simulation process.
	def start(self):
		self.__running = True

		self.sockThread1 = Thread(name='Receive1', target=self._receive_gps, args=(self.socket1, ), daemon=True)
		self.sockThread1.start()

		self.sockThread2 = Thread(name='Receive2', target=self._receive_gps, args=(self.socket2, ), daemon=True)
		self.sockThread2.start()

		self.sockThread3 = Thread(name='Receive3', target=self._receive_gps, args=(self.socket3, ), daemon=True)
		self.sockThread3.start()

		super(PositionListener,self).start()

    ## Method for stopping position listener simulation process.
	def stop(self):
		self.__running = False
		
    ## Method for running position listener simulation process.
	def run(self):
		""" 
		Update coordinates
		"""
		while self.__running:

			time.sleep(0.05)

			message = self.message[len(self.message) - 1]
			time_diff = time.time() - message[4]
			# print("Time_diff: ", time_diff)

			if message[1] >= 0 and message[2] >= 0:
				if message[0] == 1:
					X = message[1] + self.offX1
					Y = message[2] + self.offY1
				elif message[0] == 2:
					X = message[1] + self.offX2
					Y = message[2] + self.offY2
				elif message[0] == 3:
					X = message[1] + self.offX3
					Y = message[2] + self.offY3
				else:
					X = 0.0
					Y = 0.0
				
				rot = message[3]

				self.coor = (round(X), round(Y), rot)
				print(self.coor)

	def init_socket(self, PORT):
		
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #(internet, UDP)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind(('', PORT))

		return sock

	def _receive_gps(self, socket):
		
		try:
			while True:
				data,_ = socket.recvfrom(4096) # buffer size is 1024 bytes
				data = data.decode("utf-8") 
				data = json.loads(data)

				RPI_ID = data['RPI']
				x = data['x']
				y = data['y']
				rot = data['rot']
				stamp = data['timestamp']

				if x > 0.0 and y > 0.0:
					self.message.append((RPI_ID, x, y, rot, stamp))
		except KeyboardInterrupt as e:
			print(e)
			pass