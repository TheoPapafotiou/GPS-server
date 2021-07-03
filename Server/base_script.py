#!/usr/bin/env python

import os
from os.path import expanduser
import cv2
import time
import base64
from commlib.msg import PubSubMessage, DataClass
from commlib.transports.mqtt import (
	Publisher, ConnectionParameters
)
import threading

@DataClass
class ImageMessage(PubSubMessage):
    img: str = ""

class Dispatcher:
	def __init__(self):
		self.running = False
		self.image_path = os.path.join(
			expanduser("~"), "Desktop", "Random", "image.jpg"
		)
		self.delay = 1
		self.cap = cv2.VideoCapture(0)

		self.conn_params = ConnectionParameters(
			host='r4a-platform.ddns.net', 
			port=8178
		)
		self.conn_params.credentials.username = "turtlebot-1"
		self.conn_params.credentials.password = "turtlebot-1"
		self.pub = Publisher(
			topic="vroom/camera_1/image", 
			msg_type=ImageMessage, 
			conn_params=self.conn_params
		)
		self.th = threading.Thread(target = self.deploy_image_capture)
		self.th.start()

	def deploy_image_capture(self):
		frame = self.cap.read()
		cv2.imwrite({self.image_path}, frame)

	def start(self):
		self.running = True
		while self.running:
			time.sleep(self.delay)
			while not os.path.exists(self.image_path):
				print(">>> Image not got yet")
				time.sleep(1)

			print(">>> Opening file")
			with open(self.image_path, "rb") as image_file:
				encoded_string = base64.b64encode(image_file.read())
				self.msg = ImageMessage(img = encoded_string.decode("ascii"))
				print(">>> Dispatching image")
				self.pub.publish(self.msg)

d = Dispatcher()
d.start()

