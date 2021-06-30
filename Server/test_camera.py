from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.resolution = (2592, 1944)
camera.framerate = 15

for effect in camera.IMAGE_EFFECTS:
    sleep(0.5)
    camera.image_effect = effect
    print(effect)
    camera.start_preview()
    sleep(2.5)
    camera.capture('/home/pi/Desktop/'+str(effect)+'.jpg')
    camera.stop_preview()

for effect in camera.IMAGE_EFFECTS:
    sleep(0.5)
    camera.image_effect = effect
    camera.start_preview()
    sleep(1.5)
    camera.capture('/home/pi/Desktop/'+str(effect)+'.jpg')
    camera.stop_preview()