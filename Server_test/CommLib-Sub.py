import time
import cv2
import sys
import base64
import numpy as np
from commlib.msg import PubSubMessage, DataClass
from commlib.transports.mqtt import (
    Subscriber, ConnectionParameters
)
from detect_motion import objectTracking
from skimage.transform import ProjectiveTransform

tracker = objectTracking()
transformer = ProjectiveTransform()
size_of_track_w = 160 #cm
size_of_track_h = 180 #cm
init_x = 0 #cm
init_y = 0 #cm

arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_100)
arucoParams = cv2.aruco.DetectorParameters_create()
countFrames = 0
coord = np.array([])
height = 0
width = 0
interval_x = 0
interval_y = 0
points = np.zeros((5, 3))
center_x = np.zeros(4)
center_y = np.zeros(4)
bottom_left_track = np.zeros((2))
bottom_right_track = np.zeros((2))
top_left_track = np.zeros((2))
top_right_track = np.zeros((2))
correct_detection = False

def detect_ArUco_simple(frame):
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

    return cX, cY

def detect_ArUco(frame, flag, points):

    correct_detection = False
    (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, arucoDict, parameters=arucoParams)
    #print("IDs: ", ids)
    cX = 0
    cY = 0

    if len(corners) > 0:
        # flatten the ArUco IDs list
        ids = ids.flatten()
        counter = -1

        # loop over the detected ArUCo corners
        for (markerCorner, markerID) in zip(corners, ids):
            if flag == 0 and markerID != 8 and markerID != 0:
                counter += 1
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

                points[counter] = (cX, cY, markerID)

                if counter == 3:
                    correct_detection = True
            
            elif flag == 1 and markerID == 8:
                counter += 1
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

                points = np.zeros(shape=(5,3))
                points[counter] = (cX, cY, markerID)

                if cX > 0 and cY > 0:
                    correct_detection = True 

    return frame, points, correct_detection

@DataClass
class ImageMessage(PubSubMessage):
    img: str = '0'

def image_data_callback(msg):
    #print(f'Message: {msg}')
    global countFrames
    global correct_detection
    global coord
    global height
    global width
    global interval_x
    global interval_y
    global points
    global center_x
    global center_y
    global bottom_left_track
    global bottom_right_track
    global top_left_track
    global top_right_track
    
    countFrames += 1
    img_binary = base64.b64decode(msg['img'].encode('ascii'))
    img_np = np.frombuffer(img_binary, dtype=np.uint8)
    img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
    
    if countFrames == 1:
        frame_init = img
        height, width, _ = frame_init.shape

        while correct_detection is False:
            frame_init, points, correct_detection = detect_ArUco(frame_init, flag=0, points=points)
            print(points)

        for i in range(0, 4):
            index = [points[i][0], points[i][1]]
            if points[i][2] == 1:
                top_left_track = index
                print("TL: ", top_left_track)
            elif points[i][2] == 2:
                top_right_track = index
                print("TR: ", top_right_track)
            elif points[i][2] == 3:
                bottom_right_track = index
                print("BR: ", bottom_right_track)
            elif points[i][2] == 4:
                bottom_left_track = index
                print("BL: ", bottom_left_track)

        # Transform quadrilateral to rectangle
        src = np.asarray(
            [bottom_left_track, top_left_track, top_right_track, bottom_right_track])

        dst = np.asarray([
                        [(size_of_track_w - size_of_track_h)/2, size_of_track_h],
                        [(size_of_track_w - size_of_track_h)/2, 0],
                        [size_of_track_w - (size_of_track_w - size_of_track_h)/2, 0],
                        [size_of_track_w - (size_of_track_w - size_of_track_h)/2, size_of_track_h]
                        ])

        transformer_start = time.time()
        success = transformer.estimate(src, dst)
        transformer_stop = time.time()
        transformer_duration = transformer_stop - transformer_start
        if success:
            print("Duration of the transformation: " + str(transformer_duration))

        interval_x = 10*(top_right_track[0] - top_left_track[0])/size_of_track_w
        interval_y = 10*(bottom_right_track[1] - top_left_track[1])/size_of_track_h
        cv2.imwrite("Initial_frame", frame_init)

    elif countFrames >= 1:
        time.sleep(0.5)
        img, points, correct_detection = detect_ArUco(img, flag=1, points=points)
        point_car = points[0]

        if point_car[0] > 0 and point_car[1] > 0:
            gps_x = point_car[0] - top_left_track[0]
            gps_y = point_car[1] - top_left_track[1]
            actual_gps_x = init_x + (gps_x * size_of_track_w / (top_right_track[0] - top_left_track[0]))
            actual_gps_y = init_y + (gps_y * size_of_track_h / (bottom_right_track[1] - top_left_track[1]))
            cv2.putText(img, "X: "+str(int(actual_gps_x))+" & Y: "+str(int(actual_gps_y)), (int(gps_x), int(gps_y)), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 3)

        
        for k in range (int(top_left_track[0]), int(top_right_track[0]), int(interval_x)):
            cv2.line(img, (k, int(top_left_track[1])), (k, int(bottom_right_track[1])), (255, 0, 0), 1, 1)

        for p in range (int(top_left_track[1]), int(bottom_right_track[1]), int(interval_y)):
            cv2.line(img, (int(top_left_track[0]), p), (int(top_right_track[0]), p), (255, 0, 0), 1, 1)

        dim = (1280, 960)
        img_resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        cv2.imshow("Frames", img_resized)
        cv2.imwrite("test_grid_"+str(countFrames)+".png", img)
        print('The GPS coordinates are: X -> ', actual_gps_x, ' || Y -> ', actual_gps_y)
        if countFrames == 2:
            coord = np.append(coord, [gps_x, gps_y])
        else:
            coord = np.vstack((coord, [gps_x, gps_y]))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            raise Exception("Stop imshow")

    #point_x, point_y = detect_ArUco_simple(img)

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