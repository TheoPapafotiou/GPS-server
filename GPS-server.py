import cv2
import numpy as np
import time
import math
from detect_motion import objectTracking

tracker = objectTracking()
size_of_track_w = 100 #cm
size_of_track_h = 100 #cm

qrCodeDetector = cv2.QRCodeDetector()
cap = cv2.VideoCapture(0)

def detect_qr(image, mask):
    masked = cv2.bitwise_and(image, image, mask=mask)
    decodedText, points, _ = qrCodeDetector.detectAndDecode(masked)
    print('\n', points)
    return points

def center_of_points(points):
    h1_c = abs(points[0][3][1] - points[0][0][1])/2
    w1_c = abs(points[0][1][0] - points[0][0][0])/2
    #h1_c = math.dist(points[0], points[3])/2
    #w1_c = math.dist(points[0], points[1])/2
    center_x = int(points[0][0][0] + w1_c)
    center_y = int(points[0][0][1] + h1_c)
    print("Centers are: ", center_x, center_y)
    return center_x, center_y

#frame_init = cv2.imread("test_track_qr.png")
success, frame_init = cap.read()
#frame_init = cv2.flip(frame_init, 1)

height, width, _ = frame_init.shape

mask = np.zeros((4, height, width), dtype="uint8")
points = np.zeros((4, 1, 4, 2))
# decodedText = np.zeros((4, 20), str)
center_x = np.zeros(4)
center_y = np.zeros(4)
# upper left
cv2.rectangle(mask[0], (0, 0), (width//2, height//2), 255, -1)
# upper right
cv2.rectangle(mask[1], (width//2, 0), (width, height//2), 255, -1)
# down left
cv2.rectangle(mask[2], (0, height//2), (width//2, height), 255, -1)
# down right
cv2.rectangle(mask[3], (width//2, height//2), (width, height), 255, -1)

while True:
    for i in range (0, 4):
        points[i] = detect_qr(frame_init, mask[i])
        center_x[i], center_y[i] = center_of_points(points[i])
        time.sleep(0.5)
        if center_x[i] == 0 and center_y[i] == 0:
            print("QR code not detected, WTF")
            cv2.imwrite("error_qr.png", frame_init)
            break
    if (center_x[0] > 0) and (center_x[1] > 0) and (center_x[2] > 0) and (center_x[3] > 0):
        for i in range (0,4):
            frame_init = cv2.circle(frame_init, (int(center_x[i]), int(center_y[i])), radius=5, color=(0, 0, 255), thickness=1)
        cv2.imwrite("correct_init_frame.png", frame_init)
        break

# print(points[:])
for i in range (int(center_x[0]), int(center_x[1]), 20):
    cv2.line(frame_init, (i, int(center_y[0])), (i, int(center_y[2])), (255, 0, 0), 1, 1)

for i in range (int(center_y[0]), int(center_y[2]), 20):
    cv2.line(frame_init, (i, int(center_x[0])), (i, int(center_x[1])), (255, 0, 0), 1, 1)

frame1 = np.zeros((width, height))
frame2 = np.zeros((width, height))
frame3 = np.zeros((width, height))

success, frame1 = cap.read()
#frame1 = cv2.imread('test_track_qr/'+str(1)+'.png')

interval_x = 10*(center_x[1] - center_x[0])/size_of_track_w
interval_y = 10*(center_y[3] - center_y[0])/size_of_track_h

start = time.time()
count_frames = 0
while cap.isOpened():
#for j in range (2, 28):
    #time.sleep(0.1)
    frame2 = frame1
    #frame1 = cv2.imread("test_track_qr/"+str(j)+".png")
    success, frame1 = cap.read()
    frame3, point_x, point_y = tracker.objectTracking(frame1, frame2)

    if point_x == 0 and point_y == 0 and (time.time() - start > 80):
        cap.release()
    
    if point_x > 0 and point_y > 0:
        gps_x = point_x - center_x[0]
        gps_y = point_y - center_y[0]
        actual_gps_x = gps_x * size_of_track_w / (center_x[1] - center_x[0])
        actual_gps_y = gps_y * size_of_track_h / (center_y[3] - center_y[0])
        cv2.putText(frame3, "X: "+str(int(actual_gps_x))+" & Y: "+str(int(actual_gps_y)), (int(gps_x), int(gps_y)), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 3)

        
        for k in range (int(center_x[0]), int(center_x[1]), int(interval_x)):
            cv2.line(frame3, (k, int(center_y[0])), (k, int(center_y[3])), (255, 0, 0), 1, 1)

        for p in range (int(center_y[0]), int(center_y[3]), int(interval_y)):
            cv2.line(frame3, (int(center_x[0]), p), (int(center_x[1]), p), (255, 0, 0), 1, 1)

        
        cv2.imshow("Frames", frame3)
        count_frames += 1
        cv2.imwrite("test_grid_"+str(count_frames)+".png", frame3)
        print('The GPS coordinates are: X -> ', actual_gps_x, ' || Y -> ', actual_gps_y)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break