# https://learn.adafruit.com/drive-a-16x2-lcd-directly-with-a-raspberry-pi/python-code
# 120 Ohm

from time import sleep, time
from datetime import datetime
import Adafruit_CharLCD as LCD

class LCDServer():

    def __init__(self, numofTL=3):
        # TL Info
        self.TLnumber = numofTL
        self.TLstate = [-1 for i in range(self.TLnumber)]
        self.TLcolor = {"0": "R", "1": "Y", "2": "G", "-1": "N"}

        # OH Info
        self.detectedObject = 0
        self.objects = {"0": "None",
                        "1": "Stop", 
                        "2": "Priority",
                        "3": "Parking",
                        "4": "Crosswalk",
                        "5": "Hway Entry",
                        "6": "Hway Exit",
                        "7": "Roundabout",
                        "8": "One way",
                        "9": "TL",
                        "10": "Veh Road",
                        "11": "Veh Park",
                        "12": "Ped cross",
                        "13": "Ped road",
                        "14": "Roadblock",
                        "15": "Bumpy road"}
        
        lcd_columns = 16
        lcd_rows = 2
        lcd_backlight = 4

        # compatible with all versions of RPI as of Jan. 2019
        # v1 - v3B+
        lcd_rs = 25
        lcd_en = 24
        lcd_d4 = 23
        lcd_d5 = 17
        lcd_d6 = 18
        lcd_d7 = 22

        # Initialise the lcd class
        self.lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)
        
    def runLCD(self):
        self.lcd.clear()

        try:
            lcd_TLline = "TL = {" + str(self.TLcolor[str(self.TLstate[0])]) + " " + str(self.TLcolor[str(self.TLstate[1])]) + " " + \
                                        str(self.TLcolor[str(self.TLstate[2])]) + " " + str(self.TLcolor[str(self.TLstate[0])]) + "}\n"
                                        
            lcd_OHline = "Found:" + str(self.objects[str(self.detectedObject)])
            # combine both lines into one update to the display
            self.lcd.message(lcd_TLline + lcd_OHline)

        except Exception as e:
            print("Exception in lcd", e)
            self.lcd.clear()
    
    def stopLCD(self):
        self.lcd.clear()