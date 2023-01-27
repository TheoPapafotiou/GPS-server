from ObstacleHandler import oh
from TLSimulator import sim
from LocalizationServer import loc
import time 
import logging
from LCDServer import LCDServer
from pathlib import Path

print(Path("servers.py").absolute())

def runServers():

    # LCD Print
    lcdON = True
    lcd = LCDServer(numofTL=3)
    carID = 120

    try:        
        """Method for sending the simulated semaphore signals.
        """
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('root')

        # Set to true for output on LCD screen
        # Get time stamp when starting tester
        timeout_duration = 3600*2
        start_time = time.time()

        # Create broadcaster object
        Adv = sim()
        
        ObsHanServer = oh(logger)

        LocServer = loc(logger)

        # Start the broadcaster
        Adv.start()
        ObsHanServer.start()
        LocServer.start()

        # Wait until 60 seconds passed
        while (time.time()-start_time < timeout_duration):
            if lcdON:
                lcd.TLstate = [Adv.main_state, Adv.main_state, Adv.start_state, Adv.start_state]

                if ObsHanServer.markerSet.getlist():
                    
                    detected_objects = ObsHanServer.markerSet.getlist()[carID]
                    num_of_objects = len(detected_objects)

                    lcd.detectedObject = detected_objects[num_of_objects]['obstacle_id']

                lcd.runLCD()
                time.sleep(0.5)

        # Stop the broadcaster
        Adv.stop()
        LocServer.stop()
    except KeyboardInterrupt:
        lcd.stopLCD()
        Adv.stop()
        LocServer.stop()

runServers()
# runAdvertiser()
# print("Trying to run OH")
# try:
#     runOH()
# except Exception as e:
#     print("OH error = ", e)
