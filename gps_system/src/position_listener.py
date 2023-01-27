import sys
sys.path.insert(0,'.')
from threading import Thread
import time
import cv2
import socket
import json
import numpy as np
import random
import paho.mqtt.client as mqtt

topic = 'dwm/node/17b1/uplink/location'

class PositionListener(Thread):
	"""
	PositionListener simulator aims to populate position variable. 
	"""
	def __init__(self):

		self.coor = None

		broker = '192.168.0.102'
		port = 1883
		client_id = f'python-mqtt-{random.randint(0, 100)}'

		self.client = self.connect(client_id, broker, port)
		self.coor = None

		self.start_time = round(time.time(), 2)		
		self.__running = True
		
		Thread.__init__(self)

	def connect(self, client_id, broker, port):
		mqtt.Client.connected_flag = False
		client = mqtt.Client(client_id)
		client.on_connect = self.on_connect
		client.loop_start()
		print("Connecting to broker ", broker)
		client.connect(broker, port)

		return client

	def on_connect(self, client, userdata, flags, rc):
		if rc == 0:
			print("Connected to MQTT Broker!")
		else:
			print("Failed to connect, return code %d\n", rc)

	def on_message(self, client, userdata, msg):
		# print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
		data = json.loads(msg.payload.decode())
		position = data['position']
		self.coor = (round(position['x'], 2), round(position['y'], 2))
		self.quality = position['quality']

	def subscribe(self, client: mqtt):
		
		client.subscribe(topic)
		client.on_message = self.on_message

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
		Update coordinates
		"""
		while self.__running:

			self.subscribe(self.client)
			time.sleep(0.2)