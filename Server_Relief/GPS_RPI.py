import time
import cv2
import sys
import base64
import numpy as np
import math

from numpy.lib.function_base import median

class GPS:
    def __init__(self):
        ### Track Params ###
        self.size_of_track_w = 285 #440 #cm
        self.size_of_track_h = 340 #cm
        self.init_x = 0 #cm
        self.init_y = 0 #cm
        self.first_time = True
        self.first_image = np.zeros((1500, 1000))

        self.ID1 = [0, 1]
        self.ID2 = [2, 3]
        self.height_camera = 280
        self.height_human = 80
        self.camera_limits_y = 200
        self.aruco_centerBody = 29
        self.gps_H1 = (0.0, 0.0)
        self.gps_H2 = (0.0, 0.0)

        self.coord = np.array([])
        self.height = 0
        self.width = 0
        self.track_width = 0.0 #pixels
        self.track_height = 0.0 #pixels
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
        self.arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)
        self.arucoParams = cv2.aruco.DetectorParameters_create()

    def video(id, width, height):
        cap = cv2.VideoCapture(id)
        cap.set(3, width)
        cap.set(4, height)
        
        return cap

    def find_center(self, corners):
        (topLeft, topRight, bottomRight, bottomLeft) = corners
                    
        # convert each of the (x, y)-coordinate pairs to integers
        topRight = (int(topRight[0]), int(topRight[1]))
        bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
        bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
        topLeft = (int(topLeft[0]), int(topLeft[1]))

        cX = int((topLeft[0] + bottomRight[0]) / 2.0)
        cY = int((topLeft[1] + bottomRight[1]) / 2.0)
        theta_1 = math.degrees(math.atan2((topLeft[1] - bottomLeft[1]), (topLeft[0] - bottomLeft[0])))
        theta_2 = math.degrees(math.atan2((topRight[1] - bottomRight[1]), (topRight[0] - bottomRight[0])))
        
        print()
        print("Theta 1 = ", theta_1)
        print("Theta_2 = ", theta_2)
        theta = round((theta_1 + theta_2)//2, 1)
        if theta >= 0:
            theta -= 180
        elif theta < 0:
            theta += 180

        return cX, cY, theta
        
    def detect_ArUco(self, frame, flag, points):

        correct_detection = False
        correct_detection_H1 = False
        correct_detection_H2 = False
        (corners, ids, _) = cv2.aruco.detectMarkers(frame, self.arucoDict, parameters=self.arucoParams)
        
        # print("IDs: ", ids)
        cX = 0
        cY = 0
        H1_arucos = 0
        H2_arucos = 0
        theta_H1 = 0.0
        theta_H2 = 0.0

        if len(corners) > 0:
            # flatten the ArUco IDs list
            ids = ids.flatten()
            counter = -1

            # loop over the detected ArUCo corners
            for (markerCorner, markerID) in zip(corners, ids):
                if flag == 0 and markerID != self.ID1[0] and markerID != self.ID1[1] \
                    and markerID != self.ID2[0] and markerID != self.ID2[1]:
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

                    if markerID == self.ID1[0] or markerID == self.ID1[1]:
                        H1_arucos += 1
                        counter += 1

                        corners = markerCorner.reshape((4, 2))
                        cX, cY, theta_H1 = self.find_center(corners)
                        points[counter] = (cX, cY, markerID) 

                        if cX > 0 and cY > 0:
                            correct_detection_H1 = True
                    
                    if markerID == self.ID2[0] or markerID == self.ID2[1]:
                        H1_arucos += 1
                        counter += 1
                
                        corners = markerCorner.reshape((4, 2))
                        cX, cY, theta_H2 = self.find_center(corners)
                        points[counter] = (cX, cY, markerID)

                        if cX > 0 and cY > 0:
                            correct_detection_H2 = True                 

        print()
        print("H1_arucos: ", H1_arucos)
        print("H2_arucos: ", H2_arucos)
        print()

        return frame, points, correct_detection, correct_detection_H1, correct_detection_H2, H1_arucos, H2_arucos, theta_H1, theta_H2

    def actual_gps(self, point_car):
        
        final_gps_x = 0
        final_gps_y = 0

        if point_car[0] > 0 and point_car[1] > 0:
            gps_x = point_car[0] - self.top_left_track[0]
            gps_y = point_car[1] - self.top_left_track[1]
            actual_gps_x = (gps_x * self.size_of_track_w / (self.track_width))
            actual_gps_y = (gps_y * self.size_of_track_h / (self.track_height))

            #for the new system to be adopted
            final_gps_x = self.offset_x + (self.size_of_track_w - actual_gps_x)
            final_gps_y = self.offset_y + (self.size_of_track_h - actual_gps_y)
        
        return final_gps_x, final_gps_y

    def project_points(self, point_head, cameraID):
        c1 = 0
        c2 = 0

        center_cam = [[53,78],# [194, 77],
                        [181, 272]] # [322, 272]]

        #cameraID = 0

        a1 = center_cam[cameraID][0]
        a2 = center_cam[cameraID][1]
        b1 = point_head[0]
        b2 = point_head[1]

        d = math.sqrt((a1 - b1)**2 + (a2 - b2)**2)
        print("d: ", d)
        D = (d * (self.height_camera - self.height_human))/(self.height_camera)
        print("D: ", D)

        try:
            k = (b2 - a2)/(b1 - a1)
        except Exception as e:
            print(e)
            k = 0
            pass

        t = a2 - k*a1
        a = k**2 + 1
        b = 2*k*t - 2*a1 - 2*a2*k
        c = t**2 + a1**2 + a2**2 - 2*a2*t - D**2
        print("a: ", a)
        print("b: ", b)
        print("c: ", c)

        roots = self.quad_equation(a, b, c) 

        c1_0 = roots[0]
        c2_0 = k*c1_0 + t

        c1_1 = roots[1]
        c2_1 = k*c1_1 + t

        if math.sqrt((c1_0-b1)**2 + (c2_0-b2)**2) < math.sqrt((c1_1-b1)**2 + (c2_1-b2)**2):
            c1 = c1_0
            c2 = c2_0
        else:
            c1 = c1_1
            c2 = c2_1

        true_point = [c1, c2]

        return true_point

    def quad_equation(self, a, b, c):
        
        dis = b**2 - 4 * a * c 
        sqrt_val = math.sqrt(abs(dis))

        roots = [0, 0]
        
        if dis > 0:  
            roots[0] = (-b + sqrt_val)/(2 * a) 
            roots[1] = (-b - sqrt_val)/(2 * a)

        else:
            print("Error with roots!")

        return roots 

    def gps_aruco_human(self, point_head):
        
        point_head_x, point_head_y = self.actual_gps(point_head)
        print("Point_head_X, _Y: ", point_head_x, point_head_y)

        cameraID = 0
        if point_head_y < self.camera_limits_y:
            cameraID = 0
        else:
            cameraID = 1
            
        point_human = self.project_points((point_head_x, point_head_y), cameraID)
        print("Point_human: ", point_human)

        # gps_x, gps_y = self.actual_gps(point_human)

        return point_human[0], point_human[1], point_head[2]

    def turn_gps(self, gps_aruco, theta, direction):

        """
        direction = -1 --> left
        direction = +1 --> right
        """

        if abs(theta) <= 90:
            phi = 90 - abs(theta)
        else:
            phi = 90 - (180 - abs(theta))

        x_diff = self.aruco_centerBody*math.cos(phi)
        y_diff = self.aruco_centerBody*math.sin(phi)

        if 0 <= theta <= 90:
            gps_Hx = gps_aruco[0] + math.copysign(1, direction) * x_diff
            gps_Hy = gps_aruco[1] - math.copysign(1, direction) * y_diff
        elif 90 < theta <= 180:
            gps_Hx = gps_aruco[0] + math.copysign(1, direction) * x_diff
            gps_Hy = gps_aruco[1] + math.copysign(1, direction) * y_diff
        elif -90 <= theta < 0:
            gps_Hx = gps_aruco[0] - math.copysign(1, direction) * x_diff
            gps_Hy = gps_aruco[1] - math.copysign(1, direction) * y_diff
        else:
            gps_Hx = gps_aruco[0] - math.copysign(1, direction) * x_diff
            gps_Hy = gps_aruco[1] + math.copysign(1, direction) * y_diff

        gps_H = (gps_Hx, gps_Hy)

        return gps_H

    def gps_center_human(self, gps_human, H1_arucos, H2_arucos, theta_H1, theta_H2):

        if H1_arucos == 2:
            self.gps_H1 = ((gps_human[0][0] + gps_human[1][0])/2, (gps_human[0][1] + gps_human[1][1])/2)
        elif H1_arucos == 1:
            for i in range(0, 2):
                print("For i = ", i, ", it is: ", int(gps_human[i][2]) == self.ID1[0])
                if int(gps_human[i][2]) == self.ID1[0]:
                    direction = -1
                    gps_h = gps_human[i]
                elif int(gps_human[i][2]) == self.ID1[1]:
                    direction = 1
                    gps_h = gps_human[i]

            self.gps_H1 = self.turn_gps((gps_h[0], gps_h[1]), theta_H1, direction)
            print()
            print("Aruco one GPS: ", (gps_h[0], gps_h[1]))
            print("Center Human after turn: ", self.gps_H1)
            print()
        else:
            print("No Human 1 detected. Errrrrrror!")

        if H2_arucos == 2:
            self.gps_H2 = ((gps_human[2][0] + gps_human[3][0])/2, (gps_human[2][1] + gps_human[3][1])/2)
        elif H2_arucos == 1:
            for i in range(2, 4):
                if int(gps_human[i][2]) == self.ID2[0]:
                    direction = -1
                    gps_h = gps_human[i]
                elif int(gps_human[i][2]) == self.ID2[1]:
                    direction = 1
                    gps_h = gps_human[i]

            self.gps_H2 = self.turn_gps((gps_h[0], gps_h[1]), theta_H2, direction)
        else:
            print("No Human 2 detected. Errrrrrror!")

    def tracking_procedure(self, img, countFrames):
        
        if self.first_time is True:
            self.first_image = img

            cv2.imwrite("First image.jpg", self.first_image)
            self.height, self.width, _ = self.first_image.shape
            correct_detection = False

            while correct_detection is False:
                self.first_image, self.points, correct_detection, _, _, _, _, _, _ = self.detect_ArUco(self.first_image, flag=0, points=self.points)
                print(self.points)

            time_stamp = time.time()    
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

            for k in range (int(self.top_left_track[0]), int(self.bottom_right_track[0]), int(self.interval_x)):
                cv2.line(self.first_image, (k, int(self.top_left_track[1])), (k, int(self.bottom_right_track[1])), (255, 0, 0), 1, 1)

            for p in range (int(self.top_left_track[1]), int(self.bottom_right_track[1]), int(self.interval_y)):
                cv2.line(self.first_image, (int(self.top_left_track[0]), p), (int(self.bottom_right_track[0]), p), (255, 0, 0), 1, 1)

            #cv2.imwrite("Initial_frame.jpg", self.first_image)
            self.first_time = False

        if self.first_time is False:
            img, points, correct_detection, correct_detection_H1, correct_detection_H2, H1_arucos, H2_arucos, theta_H1, theta_H2 = self.detect_ArUco(img, flag=1, points=self.points)
            time_stamp = time.time()

            point_head = np.ones(shape=(5,3)) * 20
            gps_human = np.ones(shape=(4,3)) * 20
            
            if correct_detection_H1 is True or correct_detection_H2 is True:
                for k in range (int(self.top_left_track[0]), int(self.bottom_right_track[0]), int(self.interval_x)):
                    cv2.line(img, (k, int(self.top_left_track[1])), (k, int(self.bottom_right_track[1])), (255, 0, 0), 1, 1)

                for p in range (int(self.top_left_track[1]), int(self.bottom_right_track[1]), int(self.interval_y)):
                    cv2.line(img, (int(self.top_left_track[0]), p), (int(self.bottom_right_track[0]), p), (255, 0, 0), 1, 1)

                for i in range(H1_arucos + H2_arucos):
                    if points[i][2] == self.ID1[0]:
                        point_head[0] = points[i]
                        gps_human[0][0], gps_human[0][1], gps_human[0][2] = self.gps_aruco_human(point_head[0])
                    elif points[i][2] == self.ID1[1]:
                        point_head[1] = points[i]
                        gps_human[1][0], gps_human[1][1], gps_human[1][2] = self.gps_aruco_human(point_head[1])
                    elif points[i][2] == self.ID2[0]:
                        point_head[2] = points[i]
                        gps_human[2][0], gps_human[2][1], gps_human[2][2] = self.gps_aruco_human(point_head[2])
                    elif points[i][2] == self.ID2[1]:
                        point_head[3] = points[i]
                        gps_human[3][0], gps_human[3][1], gps_human[3][2] = self.gps_aruco_human(point_head[3])

            print(gps_human)
            self.gps_center_human(gps_human, H1_arucos, H2_arucos, theta_H1, theta_H2)

            print()
            if correct_detection_H1 is False:
                print("ERRRRRRROOOR H1!")
            else:
                print("GPS_H1 is -->  X = ", self.gps_H1[0], " and Y = ", self.gps_H1[1], " with theta = ", theta_H1)

            if correct_detection_H2 is False:
                print("ERRRRRRROOOR H2!") 
            else:
                print("GPS_H2 is -->  X = ", self.gps_H2[0], " and Y = ", self.gps_H2[1], " with theta = ", theta_H2)

            # cv2.circle(img, (int(point_head[0]), int(point_head[0])), radius=5, color=(0, 0, 255), thickness=-1)
            # cv2.putText(img, "X: " + str(gps_car_x) + ", Y: " + str(gps_car_y), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            # cv2.imwrite("Frame_" + str(countFrames) + '.jpg', img)

            # if countFrames == 1:
            #     self.coord = np.append(self.coord, [gps_car_x, gps_car_y])
            # else:
            #     self.coord = np.vstack((self.coord, [gps_car_x, gps_car_y]))
        
        return self.gps_H1, self.gps_H2, theta_H1, theta_H2, time_stamp


# gps = GPS()
# points = gps.project_points((360, 120))
# print(points)