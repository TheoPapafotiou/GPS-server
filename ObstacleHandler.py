from threading import Thread
import socket

from serverconfig import ServerConfig
from carclientserver import CarClientServerThread
from serverbeacon import ServerBeaconThread
from data_collector import MarkerDataSet

import logging
import time

class oh(Thread):
    """Class used for running broadcaster algorithm for simulated obstacle handler.
    """
    def __init__(self, logger):

        self.RUN_OH = False

        # Communication parameters, create and bind socket
        self.PORT = 50007
        self.BCAST_ADDRESS = '<broadcast>'

        # Create a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.server_address = (self.BCAST_ADDRESS, self.PORT)

        # Init communication with client 
        logging.basicConfig(level=logging.INFO)
        self.__logger = logging.getLogger('root')

        self.markerSet = MarkerDataSet()
        self.serverconfig = ServerConfig('<broadcast>', 23456, 23466)
        # privateKeyFile = "home/pi/Desktop/VROOM_Servers/privatekey_server_test.pem"
        privateKeyFile = "privatekey_server_test.pem"
        clientkeys = "keys/"

        self.__carclientserverThread = CarClientServerThread(self.serverconfig, self.__logger, keyfile = privateKeyFile, markerSet = self.markerSet, clientkeys = clientkeys)
        self.__beaconserverThread =  ServerBeaconThread(self.serverconfig, 1.0, self.__logger)

        Thread.__init__(self)

    def run(self):    
        self.__carclientserverThread.start()
        self.__beaconserverThread.start()
 
        try:
            while(True):
                time.sleep(1.0)
                self.__logger.info(self.markerSet.getlist())
        except KeyboardInterrupt:
            pass
             
        self.__carclientserverThread.stop()
        self.__carclientserverThread.join()
        self.__beaconserverThread.stop()
        self.__beaconserverThread.join()

    def start(self):
        """Method for starting the process.
        """
        self.RUN_OH = True

        super(oh,self).start()

    def stop(self):
        """Method for stopping the process.
        """
        # self.lcd.stopLCD()
        self.RUN_OH = False

def runOh():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('root')
    try:
        ObsHanServer = oh(logger)

        ObsHanServer.start()

    except KeyboardInterrupt:
        ObsHanServer.stop()

if __name__ == "__main__":
    runOh()
