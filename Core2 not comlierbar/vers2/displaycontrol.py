

# to do: wake up and sleep, read sesns, send data, wasserpump einschalten
# show data, show wifi connection, show time, 
# 
#

#



from machine import Pin, SPI
from machine import SoftI2C

import focaltouch
import ili9342c
import axp202c

import time
import random

import vga2_8x8 as font1
import vga2_bold_16x16 as font3
import vga2_16x16 as font2  # Hinzufügen

# Wichtige ILI9342C-Befehle
ILI9342C_SWRESET = 0x01   # Software Reset
ILI9342C_SLPIN   = 0x10   # Sleep In
ILI9342C_SLPOUT  = 0x11   # Sleep Out
ILI9342C_INVOFF  = 0x20   # Display Inversion OFF
ILI9342C_INVON   = 0x21   # Display Inversion ON
ILI9342C_DISPOFF = 0x28   # Display OFF
ILI9342C_DISPON  = 0x29   # Display ON
ILI9342C_CASET   = 0x2A   # Column Address Set
ILI9342C_PASET   = 0x2B   # Page Address Set
ILI9342C_RAMWR   = 0x2C   # RAM Write





class DisplayControl():
    
    
    def __init__(self, axp):
        
        self.reset=Pin(33, Pin.OUT)
        self.cs=Pin(5, Pin.OUT)
        self.dc=Pin(15, Pin.OUT)
        self.rotation=0
        
        
        self.i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
        self.spi = SPI(2,baudrate=10000000,sck=Pin(18),mosi=Pin(23)) # SPI init
        self.tft = ili9342c.ILI9342C(spi=self.spi, width=320, height=240, reset=self.reset,
                                     cs=self.cs, dc=self.dc, rotation=0) # Display ini
        
        self.touch = focaltouch.FocalTouch(self.i2c)
        
        self.axp = axp
        self.axp.enablePower(axp202c.AXP192_LDO2) # Display anschalten
        self.axp.setDC3Voltage(2700) # Hintergrundbeleuchtung einstellen
        
        self.tft.init() # Initialisiert und löscht das Display
        self.tft.fill(ili9342c.BLACK) # füllt das Bild weiß
        self.tft.text(font3,"Loading...",20,100,ili9342c.WHITE)
        
        self.mainScreen()
    
    def writeCmd(self, cmd, data=None): # Schickt ein 8-Bit-Kommando (cmd) + optional Daten an das Display.
        
        self.cs.value(0)  # CS auf Low => selektieren
        self.dc.value(0) # DC = 0 => Kommando
        self.spi.write(bytearray([cmd]))

        if data is not None: # Falls Daten vorhanden => DC=1 und Daten senden
            self.dc.value(1)
            if isinstance(data, int):
                self.spi.write(bytearray([data]))
            else:
                self.spi.write(data)

        self.cs.value(1) # CS => High => fertig
        
    def displayOff(self):
        self.writeCmd(ILI9342C_DISPOFF) 
 
    def displayOn(self):
        self.writeCmd(ILI9342C_DISPON) 
 
    def getTouch(self):
        return self.touch
    
    
    def isTouchActive():
        return self.touch.touched
        
        
    def displayDcOff(self):
        # 1) Hintergrundbeleuchtung ausschalten
        #self.axp.setDC3Voltage(1000)  # oder disablePower(AXP192_DCDC3)
        time.sleep_ms(50)          # kleine Wartezeit
        #self.axp.disablePower(axp202c.AXP192_LDO2)
        
    def displayDcOn(self):
        # 1) Hintergrundbeleuchtung ausschalten
        #self.axp.setDC3Voltage(1000)  # oder disablePower(AXP192_DCDC3)
        time.sleep_ms(50)          # kleine Wartezeit
        #self.axp.enablePower(axp202c.AXP192_LDO2) # Display anschalten
        
        

    def handleTouch(self):
        # Überprüfen, ob der Touch-Sensor aktiviert ist
        if self.touch.touched:  # Methode, die erkennt, ob das Display berührt wurde
            print("Touch erkannt. Display wird eingeschaltet...")
            self.displayOn()  # Display einschalten
            
            
    def energyModeOn(self):
        print("EnergyModeOn...")
        self.displayOff()
        #print("Display wurde ausgeschaltet.")
        time.sleep(2)
        self.axp.setDC3Voltage(1000)
        print("DC3 aus.")
        return False
    
    def energyModeOff(self):
        print("EnergyModeOff...")
        self.axp.setDC3Voltage(3000)
        time.sleep(2)
        self.displayOn()
        return True;
        
        
        
        
        
        
        
        
#display.mainScreen(SENSORS_DATA["TempSht40"],SENSORS_DATA["HumidSht40"],
                      # SENSORS_DATA["PressBmp"],SENSORS_DATA["LightIntens"],SENSORS_DATA["dist"])
    def mainScreen(self, temperatur = 0, humidity = 0, pressure = 0, light = 0, distance = 0):
        self.tft.fill(ili9342c.BLACK)  # Bildschirm löschen

        # Obere Statusleiste
        #self.tft.rect(11, 200, 200, 40, 0x2B58)
        #self.tft.text(font1, "Datum:", 20, 215, 0xAEBC)

        #self.tft.rect(110, 10, 100, 30, 0x2B58)
        #self.tft.text(font1, "WIFI: OK!", 120, 21, 0xAEBC)

        #self.tft.rect(210, 10, 100, 30, 0x2B58)
        #self.tft.text(font1, "AKKU:", 220, 21, 0xAEBC)

        # Sensorwerte anzeigen
        
        self.tft.rect(10, 10, 300, 230, 0x2B58)
        # Temperatur
        self.tft.text(font1, "Temperatur:", 20, 20, 0xAEBC)  # Standardfarbe
        self.tft.text(font1, f"{temperatur:.1f} °C", 150, 20, 0x07E0)  # Wert in Grün

        # Luftfeuchte
        self.tft.text(font1, "Luftfeuchte:", 20, 50, 0xAEBC)
        self.tft.text(font1, f"{humidity:.1f} %", 150, 50, 0x07E0)

        # Luftdruck
        self.tft.text(font1, "Luftdruck:", 20, 80, 0xAEBC)
        self.tft.text(font1, f"{pressure:.1f} Pa", 150, 80, 0x07E0)

        # Lichtintensität
        self.tft.text(font1, "Lichtintens.:", 20, 110, 0xAEBC)
        self.tft.text(font1, f"{light:.1f} Lux", 150, 110, 0x07E0)

        # Distanz
        self.tft.text(font1, "Distanz:", 20, 140, 0xAEBC)
        self.tft.text(font1, f"{distance:.1f} mm", 150, 140, 0x07E0)


        # Sleep-Button
        #self.tft.rect(215, 200, 95, 40, 0x2B58)
        #self.tft.text(font1, "Sleep", 235, 215, 0xAEBC)

        # Start-Button
        #self.tft.rect(10, 10, 95, 30, 0x2B58)
        #self.tft.text(font1, "Start", 30, 22, 0xAEBC)

    def startScreen(self):
        self.tft.fill(ili9342c.BLACK)
        self.tft.rect(60, 100, 200, 60, 0x2B58)
        self.tft.text(font3, "Start", 130, 120, ili9342c.WHITE)




    def checkTouch(self, x_min, x_max, y_min, y_max):
        if self.touch.touched:
            x = self.touch.touches[0]['x']
            y = self.touch.touches[0]['y']
            if x_min <= x <= x_max and y_min <= y <= y_max:
                return True
        return False


















