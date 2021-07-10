import cv2
import time
from time import sleep
from Merger import Merge_Files

Merger = Merge_Files()

def video(id, width, height):
    cap = cv2.VideoCapture(id)
    cap.set(3, width)
    cap.set(4, height)
    
    return cap

cap0 = video(0, 960, 540)
print(cap0.get(3))
print(cap0.get(4))
sleep(2)
cap2 = video(2, 960, 540)
print(cap2.get(3))
print(cap2.get(4))
sleep(2)

res_size = (2304//3, 1536//3)

if cap0 is None:
    print("Error in cap0")
    cap0.release()
if cap2 is None:
    print("Error in cap2")
    cap2.release()

for k in range(0, 10):
    sleep(0.1)
    start = time.time()
    _, frame0 = cap0.read()
#     frame0 = cv2.resize(frame0, res_size, interpolation = cv2.INTER_AREA)
    _, frame2 = cap2.read()
#     frame2 = cv2.resize(frame2, res_size, interpolation = cv2.INTER_AREA)
    
    merged_frame = Merger.get_merged_frame(frame0, frame2)
    print("Procedure Duration: ", time.time() - start)


cv2.imwrite("Merged_frame_Aruco_car5.jpg", merged_frame)
cv2.imwrite("Frame0.jpg", frame0)
cv2.imwrite("Frame2.jpg", frame2)
cap0.release()
cap2.release()
