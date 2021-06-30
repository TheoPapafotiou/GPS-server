import cv2
import sys
import numpy as np
import time
import math

from numpy.core.fromnumeric import shape

size_of_track_w = 610 #cm
size_of_track_h = 405 #cm

frame = cv2.imread("Test-track/test_track_draw.jpg")
height, width, _ = frame.shape
print(height, width)

interval_x = 15*(width)/size_of_track_w
interval_y = 15*(height)/size_of_track_h

for k in range (0, int(width), int(interval_x)):
    cv2.line(frame, (k, 0), (k, int(height)), (255, 0, 255), 2, 1)

for p in range (0, int(height), int(interval_y)):
    cv2.line(frame, (0, p), (int(width), p), (255, 0, 255), 2, 1)

cv2.circle(frame, (int(width-(0*interval_x/4)), int(height-(interval_y/10))), radius=20, color=(0, 255, 255), thickness=-1)
        
cv2.imwrite("track_grid.png", frame)