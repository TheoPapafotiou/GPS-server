import cv2
from picamera import PiCamera
from time import sleep

#cap = cv2.VideoCapture(1)
arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_100)
arucoParams = cv2.aruco.DetectorParameters_create()
camera = PiCamera()

camera.resolution = (2592, 1944)
camera.framerate = 15

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
countFrames = 0
camera.start_preview()
while 1:
    #success, img = cap.read()
    camera.capture('max.jpg')
    img = cv2.imread('max.jpg')
    img, point_x, point_y = detect_ArUco(img)
    cv2.imshow("Frame", img)
    
    countFrames+=1
    if cv2.waitKey(1) & 0xFF == ord('q'):
        camera.stop_preview()
        break