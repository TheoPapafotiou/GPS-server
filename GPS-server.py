import cv2
import sys
import numpy as np
import time
import math

from numpy.core.fromnumeric import shape
from detect_motion import objectTracking
from skimage.transform import ProjectiveTransform
import matplotlib.pyplot as plt

tracker = objectTracking()
transformer = ProjectiveTransform()
size_of_track_w = 100 #cm
size_of_track_h = 40 #cm

qrCodeDetector = cv2.QRCodeDetector()
arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_100)
arucoParams = cv2.aruco.DetectorParameters_create()
cap = cv2.VideoCapture(1)

def detect_qr(image, mask):
    masked = cv2.bitwise_and(image, image, mask=mask)
    decodedText, points, _ = qrCodeDetector.detectAndDecode(masked)
    print('\n', points, '\n')
    return points

def center_of_QR(points):
    h1_c = abs(points[0][3][1] - points[0][0][1])/2
    w1_c = abs(points[0][1][0] - points[0][0][0])/2
    #h1_c = math.dist(points[0], points[3])/2
    #w1_c = math.dist(points[0], points[1])/2
    center_x = int(points[0][0][0] + w1_c)
    center_y = int(points[0][0][1] + h1_c)
    print("Centers are: ", center_x, center_y)
    return center_x, center_y

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


#frame_init = cv2.imread("Test-track/test_track_qr.png")
success, frame_init = cap.read()
#frame_init = cv2.flip(frame_init, 1)
height, width, _ = frame_init.shape

points = np.zeros((5, 3))
center_x = np.zeros(4)
center_y = np.zeros(4)
bottom_left_track = np.zeros((2))
bottom_right_track = np.zeros((2))
top_left_track = np.zeros((2))
top_right_track = np.zeros((2))

time.sleep(1)
correct_detection = False
while correct_detection is False:
    success, frame_init = cap.read()
    #frame_init = cv2.flip(frame_init, 1)
    frame_init, points, correct_detection = detect_ArUco(frame_init, flag=0, points=points)
    print(points)
    time.sleep(1)

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

# Frames initialization
frame = np.zeros((width, height))

success, frame = cap.read()
#frame1 = cv2.imread("Test-track/"+str(1)+".png")

interval_x = 10*(top_right_track[0] - top_left_track[0])/size_of_track_w
interval_y = 10*(bottom_right_track[1] - top_left_track[1])/size_of_track_h

start = time.time()
count_frames = 0

coord = np.array([])

while cap.isOpened():
#for j in range (2, 28):

    time.sleep(0.5)
    #frame = cv2.imread("Test-track/"+str(j)+".png")
    success, frame = cap.read()
    frame, points, correct_detection = detect_ArUco(frame, flag=1, points=points)
    point_car = points[0]

    if point_car[0] == 0 and point_car[1] == 0 and (time.time() - start > 80):
        cap.release()
    
    if point_car[0] > 0 and point_car[1] > 0:
        gps_x = point_car[0] - top_left_track[0]
        gps_y = point_car[1] - top_left_track[1]
        actual_gps_x = gps_x * size_of_track_w / (top_right_track[0] - top_left_track[0])
        actual_gps_y = gps_y * size_of_track_h / (bottom_right_track[1] - top_left_track[1])
        cv2.putText(frame, "X: "+str(int(actual_gps_x))+" & Y: "+str(int(actual_gps_y)), (int(gps_x), int(gps_y)), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 3)

        
        for k in range (int(top_left_track[0]), int(top_right_track[0]), int(interval_x)):
            cv2.line(frame, (k, int(top_left_track[1])), (k, int(bottom_right_track[1])), (255, 0, 0), 1, 1)

        for p in range (int(top_left_track[1]), int(bottom_right_track[1]), int(interval_y)):
            cv2.line(frame, (int(top_left_track[0]), p), (int(top_right_track[0]), p), (255, 0, 0), 1, 1)

        
        cv2.imshow("Frames", frame)
        count_frames += 1
        cv2.imwrite("test_grid_"+str(count_frames)+".png", frame)
        print('The GPS coordinates are: X -> ', actual_gps_x, ' || Y -> ', actual_gps_y)
        if count_frames == 1:
            coord = np.append(coord, [gps_x, gps_y])
        else:
            coord = np.vstack((coord, [gps_x, gps_y]))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

print(coord)
data = np.asarray(coord)
data_trans = transformer(data)

plt.figure()
x1 = src[[0,1,2,3,0], 0]
y1 = src[[0,1,2,3,0], 1]
x2 = data.T[0]
y2 = data.T[1]
plt.plot(x1, y1, '-')
plt.plot(x2, y2, 'o')
plt.axis([min(x1),max(x1),max(y1),min(y1)])
plt.grid(True)
plt.figure()
x1 = dst[[0,1,2,3,0], 0]
y1 = dst[[0,1,2,3,0], 1]
x2 = data_trans.T[0]
y2 = data_trans.T[1]
plt.plot(x1, y1, '-')
plt.plot(x2, y2, 'o')
plt.axis([min(x1),max(x1),max(y1),min(y1)])
plt.grid(True)
plt.show()