from threading import Thread
import logging
import time
from gps_system.src.carclientserver import CarClientServerThread
from gps_system.src.serverconfig import ServerConfig
from gps_system.src.serverbeacon import ServerBeaconThread
from gps_system.src.generatedata import GenerateData


class loc(Thread):

    def __init__(self, logger):
        self.RUN_LOC = False

        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('root')

        self.serverconfig = ServerConfig('<broadcast>', 12345, 12356)
        
        self.__generateData = GenerateData()
        privateKeyFile = "gps_system/src/privatekey_server_test.pem"
        
        self.__carclientserverThread = CarClientServerThread(self.serverconfig, logger, keyfile=privateKeyFile, markerSet=self.__generateData)
        self.__beaconserverThread =  ServerBeaconThread(self.serverconfig, 1.0, logger)

        Thread.__init__(self)

    def run(self):    
        self.__carclientserverThread.start()
        self.__beaconserverThread.start()
        self.__generateData.start()

        try:
            while(True):
                time.sleep(2.0)
        except KeyboardInterrupt:
            pass
            
        self.__carclientserverThread.stop()
        self.__carclientserverThread.join()
        self.__beaconserverThread.stop()
        self.__beaconserverThread.join()

        self.__generateData.stop()
        self.__generateData.join()

    def start(self):
        """Method for starting the process.
        """
        self.RUN_LOC = True

        super(loc,self).start()

    def stop(self):
        """Method for stopping the process.
        """
        self.RUN_LOC = False