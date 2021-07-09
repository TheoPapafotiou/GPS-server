import cv2
import time
from time import sleep
from Merger import Merge_Files

Merger = Merge_Files()
cap0 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(2)
sleep(4)

for k in range(0, 4):
    
    start = time.time()
    _, frame0 = cap0.read()
    _, frame2 = cap2.read()

    merged_frame = Merger.get_merged_frame(frame0, frame2)
    print("Procedure Duration: ", time.time() - start)


cv2.imwrite("Merged_frame", merged_frame)
