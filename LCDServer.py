# https://learn.adafruit.com/drive-a-16x2-lcd-directly-with-a-raspberry-pi/python-code
# 120 Ohm

from subprocess import Popen, PIPE
from time import sleep, time
from datetime import datetime
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

class LCD():

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
        
        self.lcd_columns = 16
        self.lcd_rows = 2

        # compatible with all versions of RPI as of Jan. 2019
        # v1 - v3B+
        self.lcd_rs = digitalio.DigitalInOut(board.D22)
        self.lcd_en = digitalio.DigitalInOut(board.D17)
        self.lcd_d4 = digitalio.DigitalInOut(board.D25)
        self.lcd_d5 = digitalio.DigitalInOut(board.D24)
        self.lcd_d6 = digitalio.DigitalInOut(board.D23)
        self.lcd_d7 = digitalio.DigitalInOut(board.D18)

        # Initialise the lcd class
        self.lcd = characterlcd.Character_LCD_Mono(self.lcd_rs, self.lcd_en, self.lcd_d4, self.lcd_d5, self.lcd_d6,
                                            self.lcd_d7, self.lcd_columns, self.lcd_rows)
        
    def runLCD(self):
        self.lcd.clear()

        try:
            lcd_TLline = "TL = {" + str(self.TLcolor[str(self.TLstate[0])]) + " " + str(self.TLcolor[str(self.TLstate[1])]) + " " + str(self.TLcolor[str(self.TLstate[2])]) + "}\n"
            lcd_OHline = "Found:" + str(self.objects[str(self.detectedObject)])
            # combine both lines into one update to the display
            self.lcd.message = lcd_TLline + lcd_OHline

        except Exception as e:
            print("Exception in lcd", e)
            self.lcd.clear()
    
    def stopLCD(self):
        self.lcd.clear()