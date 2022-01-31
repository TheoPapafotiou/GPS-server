# Module imports
import time,sys
import math
from threading import Thread
# Module used for communication
import socket
import os
import sys
from itertools import cycle
import json

from LCDServer import LCD

class sim(Thread):

    def __init__(self):
        """Class used for running broadcaster algorithm for simulated semaphores.
        """
        
        #: Flag indincating thread state
        self.RUN_ADV = False
        
        # Communication parameters, create and bind socket
        self.PORT = 50007
        self.BCAST_ADDRESS = '<broadcast>'

        # Create a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.server_address = (self.BCAST_ADDRESS, self.PORT)

        #: Patterns to be sent
        self.pattern_main = [0,0,0,0,0,1,1,2,2,2,2,2,1,1]
        self.pattern_start = [2,2,2,2,2,1,1,0,0,0,0,0,1,1]

        #: Cycles of patterns
        self.maincycle = cycle(self.pattern_main)
        self.startcycle = cycle(self.pattern_start)

        self.main_state = 0
        self.start_state = 0
        # Debug msg
        print("Created advertiser")

        # # LCD Print
        # self.lcdON = True
        # self.lcd = LCD(numofTL=3)

        Thread.__init__(self)

    def run(self):
        """Method for running the simulation.
        """
        
        # Initializations
        old_time = time.time()
        self.main_state = next(self.maincycle)
        self.start_state = next(self.startcycle)

        # Send broadcast messages
        while self.RUN_ADV:
            
            #: Change pattern element each second
            if ((time.time()-old_time)>1):
                self.main_state = next(self.maincycle)
                self.start_state = next(self.startcycle)
                old_time = time.time()

            #: Send the data each 0.1 s
            try:
                # send the data for each semaphore
                self.sendState(1,self.main_state)
                self.sendState(2,self.main_state)
                self.sendState(3, self.start_state)
            except Exception as e:
                print("Sending data failed with error: " + str(e))

            # if self.lcdON:
            #     self.lcd.TLstate = [self.main_state, self.main_state, self.start_state]
            #     self.lcd.runLCD()

            # wait for 0.1 s before next broadcast msg
            time.sleep(0.1)

    def start(self):
        """Method for starting the process.
        """
        self.RUN_ADV = True

        super(sim,self).start()


    def stop(self):
        """Method for stopping the process.
        """
        # self.lcd.stopLCD()
        self.RUN_ADV = False

    # 
    #  @param self          The object pointer.
    #  @param id            
    #  @param          
    def sendState(self,id,state):
        """Method that sends the ID and semaphore state.
        :param ID: The semaphore ID
        :type ID: int
        :param state: The semaphore state (0 - RED, 1 - Yellow, 2 - Green)
        :type state: int
        """

        # Send data
        value = {"id":id, "state":state}
        message = json.dumps(value)
        # Debug message
        # print('sending {!r}'.format(message))
        sent = self.sock.sendto(message.encode('utf-8'), self.server_address)

def runAdvertiser():
    try:        
        """Method for sending the simulated semaphore signals.
        """
        # Set to true for output on LCD screen
        # Get time stamp when starting tester
        timeout_duration = 60
        start_time = time.time()
        # Create broadcaster object
        Adv = sim()

        # Start the broadcaster
        Adv.start()

        # Wait until 60 seconds passed
        while (time.time()-start_time < timeout_duration):
            time.sleep(0.5)
        # Stop the broadcaster
        Adv.stop()
    except KeyboardInterrupt:
        Adv.stop()

if __name__ == "__main__":
    runAdvertiser()