import os
import time

countFrames = 0
while True:
    countFrames += 1
    os.system("fswebcam --no-banner -r 640x480 /home/pi/Desktop/Random/image"+str(countFrames)+".jpg")
    time.sleep(1)