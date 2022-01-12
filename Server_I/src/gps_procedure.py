import cv2
import numpy as np

class GPS_PROC:
    def __init__(self, params):
        
        self.params = params

        ### Track Params ###
        self.track_width_cm = self.params["track_width"] #cm
        self.track_height_cm = self.params["track_height"] #cm
        self.track_width_pt = 0.0 #pixels
        self.track_height_pt = 0.0 #pixels
        
        ### General Params ###
        self.first_time = True
        self.coord = np.array([])
        self.height = 0
        self.width = 0
        
        ## Design Details ###
        self.interval_x = 0
        self.interval_y = 0
        self.offset_x = 0
        self.offset_y = 0

        ### ArUCo Lists ###
        self.points = np.zeros((5, 3))
        self.bottom_left_track = np.zeros((2))
        self.bottom_right_track = np.zeros((2))
        self.top_left_track = np.zeros((2))
        self.top_right_track = np.zeros((2))

        ### Aruco Params ###
        self.arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_100)
        self.arucoParams = cv2.aruco.DetectorParameters_create()

    def find_center(self, corners):
        (topLeft, topRight, bottomRight, bottomLeft) = corners
                    
        # convert each of the (x, y)-coordinate pairs to integers
        topRight = (int(topRight[0]), int(topRight[1]))
        bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
        bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
        topLeft = (int(topLeft[0]), int(topLeft[1]))

        cX = int((topLeft[0] + bottomRight[0]) / 2.0)
        cY = int((topLeft[1] + bottomRight[1]) / 2.0)

        return cX, cY
        
    def detect_ArUco(self, frame, flag, points):

        correct_detection = False
        (corners, ids, _) = cv2.aruco.detectMarkers(frame, self.arucoDict, parameters=self.arucoParams)
        
        cX = 0
        cY = 0

        if len(corners) > 0:
            # flatten the ArUco IDs list
            ids = ids.flatten()
            counter = -1

            # loop over the detected ArUCo corners
            for (markerCorner, markerID) in zip(corners, ids):
                
                if flag == 0 and markerID != self.params["ID_car"]:
                    
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
                
                elif flag == 1:
                    
                    if markerID == self.params["ID_car"]:
                        
                        counter = 0
                
                        corners = markerCorner.reshape((4, 2))
                        cX, cY = self.find_center(corners)
                        points[counter] = (cX, cY, markerID)                 

                    if cX > 0 and cY > 0:
                        correct_detection = True 

        return frame, points, correct_detection

    def actual_gps(self, point_car):
        
        final_gps_x = 0
        final_gps_y = 0

        if point_car[0] > 0 and point_car[1] > 0:
            gps_x = point_car[0] - self.top_left_track[0]
            gps_y = point_car[1] - self.top_left_track[1]
            actual_gps_x = (gps_x * self.track_width_cm / (self.track_width_pt))
            actual_gps_y = (gps_y * self.track_height_cm / (self.track_height_pt))

            #for the new system to be adopted
            final_gps_x = self.offset_x + (self.track_width_cm - actual_gps_x)
            final_gps_y = self.offset_y + (self.track_height_cm - actual_gps_y)
        
        return final_gps_x, final_gps_y

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
                if self.points[i][2] == self.params["ID1"]:
                    self.top_left_track = index
                    print("TL: ", self.top_left_track)
                elif self.points[i][2] == self.params["ID2"]:
                    self.top_right_track = index
                    print("TR: ", self.top_right_track)
                elif self.points[i][2] == self.params["ID3"]:
                    self.bottom_right_track = index
                    print("BR: ", self.bottom_right_track)
                elif self.points[i][2] == self.params["ID4"]:
                    self.bottom_left_track = index
                    print("BL: ", self.bottom_left_track)

            self.track_width_pt = self.bottom_right_track[0] - self.top_left_track[0]
            self.track_height_pt = self.bottom_right_track[1] - self.top_left_track[1]

            self.interval_x = 10*(self.bottom_right_track[0] - self.top_left_track[0])/self.track_width_cm
            self.interval_y = 10*(self.bottom_right_track[1] - self.top_left_track[1])/self.track_height_cm

            cv2.imwrite("Initial_processed_frame.jpg", frame_init)
            self.first_time = False

        if self.first_time is False:
            
            img, points, correct_detection = self.detect_ArUco(img, flag=1, points=self.points)
            point_car = points[0]

            gps_car_x, gps_car_y = self.actual_gps(point_car)

            print('\n\nThe car GPS coordinates are: X -> ', gps_car_x, ' || Y -> ', gps_car_y)

            if countFrames == 1:
                self.coord = np.append(self.coord, [gps_car_x, gps_car_y])
            else:
                self.coord = np.vstack(self.coord, [gps_car_x, gps_car_y])
        
        return self.coord[len(self.coord)-1] 