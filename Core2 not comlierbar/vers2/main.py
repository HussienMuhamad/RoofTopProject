#System libs
import machine
import time

from machine import Pin, SoftI2C, deepsleep, Timer


#Hardware libs
import ili9342c
import axp202c
import focaltouch

#Eigene Libs
from displaycontrol import DisplayControl
from systemcheck import SystemCheck
from sensorcontrol import SensorControl
#from wificontrol import WifiControl


 
def main():
    
    #Variablen
    
    TCA9548A_ADD = 0x70
    SENSORS_LIST = []
    
    timeOut = 20000 # Wenn mehr als 10 Minuten vergangen sind (6000000 ms)
    lastTouchedTime = time.ticks_ms() # Last Touched Time
    energyModeOff = True
    energyModeCycleTime = 5 #????
    
    touchPosX = 0
    touchPosY = 0
    
    #Einbindungen
    axp = axp202c.PMU(address=0x34) # PMU einbinden
    i2c = SoftI2C(scl=Pin(33), sda=Pin(32)) # Initialisiere I2C für Sensoren und Module
    
    axp.enablePower(axp202c.AXP192_EXTEN) # mother father
    
    #Klassen initialisieren
    display = DisplayControl(axp)
    sysCheck = SystemCheck(i2c, TCA9548A_ADD) # Sensoren initialisieren
    
    
    
    #MC Check und Vorbereitungen
    
    sysCheck.lokateSensors()
    SENSORS_LIST = sysCheck.getSensListAsInt()
    print(SENSORS_LIST)

    sensors = SensorControl(i2c, SENSORS_LIST)
    
    #wifi = WifiControl()
    #wifi.connectWifi()
    
    
    touch = display.getTouch()
    
    def mycallback(timer):
        print("Hier ist call back")
        sensors = SensorControl(i2c, SENSORS_LIST)
        SENSORS_DATA = sensors.getSensorsData()
        print("TempSht:", SENSORS_DATA["TempSht40"], "°C", "HumidSht:", SENSORS_DATA["HumidSht40"], "%")
        print("Pressure:", SENSORS_DATA["PressBmp"])
        print("Light:", SENSORS_DATA["LightIntens"], "Lux")
        print("Distance:", SENSORS_DATA["dist"], "mm")
        display.mainScreen(SENSORS_DATA["TempSht40"], SENSORS_DATA["HumidSht40"],
                        SENSORS_DATA["PressBmp"], SENSORS_DATA["LightIntens"], SENSORS_DATA["dist"])
        
    
    timer = Timer(-1)
    timer.init(mode=Timer.PERIODIC, period=6000, callback=mycallback)
    
    
    
    while True:
        
        currentTime = time.ticks_ms()
        
        k = touch.touched
        if k!= 0:
            lastTouchedTime = time.ticks_ms()
            touchPosX = touch.touches[0]['x']
            touchPosY = touch.touches[0]['y']
            print('X: ',touchPosX,', y: ',touchPosY)
        
        elapsed = time.ticks_diff(currentTime, lastTouchedTime)
        if elapsed > timeOut and  energyModeOff:
            print("Mehr als 10 Minuten vergangen – führe Aktion aus!")
            energyModeOff = display.energyModeOn()
        if k!=0 and not energyModeOff:
            energyModeOff = display.energyModeOff()
        
        # Warte eine Sekunde, bevor du erneut prüfst
        time.sleep(0.1)
        print("Code leuft weiter!")







        
        


























if __name__ == "__main__":
    main() 