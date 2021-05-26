import time
import cv2
import base64
import numpy as np
from commlib.msg import PubSubMessage, DataClass
from commlib.transports.mqtt import (
    Subscriber, ConnectionParameters
)

arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_100)
arucoParams = cv2.aruco.DetectorParameters_create()

def detect_ArUco(frame):
    (corners, ids, rejected) = cv2.aruco.detectMarkers(frame,
        arucoDict, parameters=arucoParams)
    print(ids)
    #print(corners)
    cX = 0
    cY = 0

    if len(corners) > 0:
        # flatten the ArUco IDs list
        ids = ids.flatten()

        # loop over the detected ArUCo corners
        for (markerCorner, markerID) in zip(corners, ids):
            # marker corners are always returned in top-left, top-right, bottom-right and bottom-left order
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            
            # convert each of the (x, y)-coordinate pairs to integers
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))

            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(frame, (int(cX), int(cY)), radius=5, color=(0, 0, 255), thickness=-1)
            cv2.putText(frame, str(markerID), (topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return frame, cX, cY

@DataClass
class ImageMessage(PubSubMessage):
    img: str = '0'

def image_data_callback(msg):
    #print(f'Message: {msg}')
    
    img_binary = base64.b64decode(msg['img'].encode('ascii'))
    img_np = np.frombuffer(img_binary, dtype=np.uint8)
    img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
    cv2.imwrite("Image_rpi3.png", img)
    img, point_x, point_y = detect_ArUco(img)
    cv2.imshow("Frame", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        exit()

if __name__ == "__main__":
    topic = "vroom/camera_1/image"
    conn_params = ConnectionParameters(host='r4a-platform.ddns.net', port=8178)
    conn_params.credentials.username = "turtlebot-1"
    conn_params.credentials.password = "turtlebot-1"
    sub = Subscriber(topic=topic,
                    on_message=image_data_callback,
                    conn_params=conn_params)
    sub.run()
    while True:
        time.sleep(0.001)