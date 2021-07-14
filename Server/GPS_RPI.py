import time
import cv2
import sys
import base64
import numpy as np

class GPS:
    def __init__(self):
        ### Track Params ###
        self.size_of_track_w = 530 #cm
        self.size_of_track_h = 400 #cm
        self.init_x = 0 #cm
        self.init_y = 0 #cm
        self.first_time = True

        self.coord = np.array([])
        self.height = 0
        self.width = 0
        self.track_width = 0.0
        self.track_height = 0.0
        self.interval_x = 0
        self.interval_y = 0
        self.offset_x = 0
        self.offset_y = 0
        self.points = np.zeros((5, 3))
        self.center_x = np.zeros(4)
        self.center_y = np.zeros(4)
        self.bottom_left_track = np.zeros((2))
        self.bottom_right_track = np.zeros((2))
        self.top_left_track = np.zeros((2))
        self.top_right_track = np.zeros((2))

        ### Aruco Params ###
        self.arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_100)
        self.arucoParams = cv2.aruco.DetectorParameters_create()

    def video(id, width, height):
        cap = cv2.VideoCapture(id)
        cap.set(3, width)
        cap.set(4, height)
        
        return cap

    def detect_ArUco_simple(self, frame):
        (corners, ids, rejected) = cv2.aruco.detectMarkers(frame,
            self.arucoDict, parameters=self.arucoParams)
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
        
    def detect_ArUco(self, frame, flag, points):

        correct_detection = False
        (corners, ids, _) = cv2.aruco.detectMarkers(frame, self.arucoDict, parameters=self.arucoParams)
        #print("IDs: ", ids)
        cX = 0
        cY = 0

        if len(corners) > 0:
            # flatten the ArUco IDs list
            ids = ids.flatten()
            counter = -1

            # loop over the detected ArUCo corners
            for (markerCorner, markerID) in zip(corners, ids):
                if flag == 0 and markerID != 10:
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
                
                elif flag == 1 and markerID == 10:
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

    def tracking_procedure(self, img, countFrames):
        
        if self.first_time is True:
            frame_init = img
            cv2.imwrite("First image.jpg", frame_init)
            self.height, self.width, _ = frame_init.shape
            correct_detection = False

            while correct_detection is False:
                frame_init, self.points, correct_detection = self.detect_ArUco(frame_init, flag=0, points=self.points)
                print(self.points)

            for i in range(0, 4):
                index = [self.points[i][0], self.points[i][1]]
                if self.points[i][2] == 6:
                    self.top_left_track = index
                    print("TL: ", self.top_left_track)
                elif self.points[i][2] == 7:
                    self.top_right_track = index
                    print("TR: ", self.top_right_track)
                elif self.points[i][2] == 9:
                    self.bottom_right_track = index
                    print("BR: ", self.bottom_right_track)
                elif self.points[i][2] == 8:
                    self.bottom_left_track = index
                    print("BL: ", self.bottom_left_track)

            self.track_width = self.bottom_right_track[0] - self.top_left_track[0]
            self.track_height = self.bottom_right_track[1] - self.top_left_track[1]

            self.interval_x = 10*(self.bottom_right_track[0] - self.top_left_track[0])/self.size_of_track_w
            self.interval_y = 10*(self.bottom_right_track[1] - self.top_left_track[1])/self.size_of_track_h

            cv2.imwrite("Initial_frame.jpg", frame_init)
            self.first_time = False

        if self.first_time is False:
            img, points, correct_detection = self.detect_ArUco(img, flag=1, points=self.points)
            point_car = points[0]

            if point_car[0] > 0 and point_car[1] > 0:
                gps_x = point_car[0] - self.top_left_track[0]
                gps_y = point_car[1] - self.top_left_track[1]
                actual_gps_x = self.offset_x + (gps_x * self.size_of_track_w / (self.bottom_right_track[0] - self.top_left_track[0]))
                actual_gps_y = self.offset_y + (gps_y * self.size_of_track_h / (self.bottom_right_track[1] - self.top_left_track[1]))

                #for the new system to be adopted
                actual_gps_x = self.track_width - actual_gps_x
                actual_gps_y = self.track_height - actual_gps_y

                cv2.putText(img, "X: "+str(int(actual_gps_x))+" & Y: "+str(int(actual_gps_y)), (int(gps_x), int(gps_y)), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (40, 255, 40), 3)

            
            for k in range (int(self.top_left_track[0]), int(self.bottom_right_track[0]), int(self.interval_x)):
                cv2.line(img, (k, int(self.top_left_track[1])), (k, int(self.bottom_right_track[1])), (140, 48, 136), 1, 1)

            for p in range (int(self.top_left_track[1]), int(self.bottom_right_track[1]), int(self.interval_y)):
                cv2.line(img, (int(self.top_left_track[0]), p), (int(self.bottom_right_track[0]), p), (140, 48, 136), 1, 1)


            cv2.imwrite("test_grid_"+str(countFrames)+".png", img)
            print('The GPS coordinates are: X -> ', actual_gps_x, ' || Y -> ', actual_gps_y)
            if countFrames == 1:
                self.coord = np.append(self.coord, [actual_gps_x, actual_gps_y])
            else:
                self.coord = np.vstack((self.coord, [actual_gps_x, actual_gps_y]))
        
        return actual_gps_x, actual_gps_y#self.coord[len(self.coord)-1] 