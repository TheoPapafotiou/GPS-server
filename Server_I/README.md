
# After the USB plug into RPI
- In order to check the camera port...
```sh
fsusb
```
# After the installation of OpenCV
After the perfect procedure explained [in this page](https://linuxize.com/post/how-to-install-opencv-on-raspberry-pi/), you should do the following in order to import properly OpenCV:

- Some minor problems need to be changed... 
```sh
sudo mv cv2.cpython-39-arm-linux-gnueabihf.so cv2.so
```
- You need to add the path, so you can access OpenCV properly
```sh 
sudo nano ~/.bashrc
export PYTHONPATH=/usr/local/lib/python3.9/site-packages:$PYTHONPATH
```