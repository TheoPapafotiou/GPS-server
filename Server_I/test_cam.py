import cv2
import time

cap = cv2.VideoCapture(0)

countFrames = 0
while True:
    countFrames += 1
    start = time.time()
    _, frame = cap.read()
    print("Image Saved using ", time.time() - start, " secs")

    cv2.imwrite("Preview_"+str(countFrames)+".jpg", frame)
    

    if countFrames == 10:
        break

    time.sleep(0.01)

cap.release()
