# python3.6

import random
import time
import json
import paho.mqtt.client as mqtt


broker = '192.168.0.102'
port = 1883
topic = 'dwm/node/17b1/uplink/location'
client_id = f'python-mqtt-{random.randint(0, 100)}'

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)


def connect_mqtt() -> mqtt:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt):
    def on_message(client, userdata, msg):
        # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        data = json.loads(msg.payload.decode())
        position = data['position']
        print('X: {}, Y: {} || Q: {}'.format(position['x'], position['y'], position['quality']))

    client.subscribe(topic)
    client.on_message = on_message

def run():

    mqtt.Client.connected_flag = False
    client = mqtt.Client(client_id)
    client.on_connect = on_connect
    client.loop_start()
    
    print("Connecting to broker ", broker)
    client.connect(broker, port)
    while not client.connected_flag:
        subscribe(client)
        time.sleep(0.1)
    print("In Main Loop")
    client.loop_stop()     
    client.disconnect() 

if __name__ == '__main__':
    run()