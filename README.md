# Run the **updated** GPS-Server
In order to run and receive coordinates from the GPS-server, you should follow the steps below:
- Plug in the Power Adaptors of the RPIs (photo TBD).

[The scripts `rpi_gps_i.py` run on each RPI after boot, so you don't need to do anything on the RPIs]
- Clone the repo
```sh
git clone https://github.com/TheoPapafotiou/VROOM_Servers.git
git checkout GPS-server
```
- Get in the folder of the new server
```sh
cd <path_of_repo>/VROOM_servers/Server_I
```
- Run the script
```sh
python3 host_gps.py
```
And you are done!

# On GPS-RPIs (<u>**ONLY**</u> for debugging)
## IP-addresses
- 192.168.0.102
- 192.168.0.107
- 192.168.0.108

## After the USB plug into RPI
In order to check that the camera is recognized correctly
```sh
lsusb
```
## After the installation of OpenCV
After the perfect procedure explained [in this page](https://linuxize.com/post/how-to-install-opencv-on-raspberry-pi/), you should do the following in order to import properly OpenCV:

### Some minor problems need to be changed... 
```sh
sudo mv cv2.cpython-39-arm-linux-gnueabihf.so cv2.so
```
### You need to add the Python path, so you can access OpenCV properly
```sh 
sudo nano ~/.bashrc
```
Add the following line at the end of the file
```sh
export PYTHONPATH=/usr/local/lib/python3.9/site-packages:$PYTHONPATH
```
Save and source the file
```sh
source ~/.bashrc
```