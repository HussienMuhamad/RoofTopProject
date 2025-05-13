

import network
import socket
import time
import axp202c



from machine import Pin, SoftI2C, Timer

from machine import Pin, I2C
from vl53l0x import VL53L0X

#Einbindungen
axp = axp202c.PMU(address=0x34) # PMU einbinden
i2c = SoftI2C(scl=Pin(33), sda=Pin(32)) # Initialisiere I2C für Sensoren und Module

axp.enablePower(axp202c.AXP192_EXTEN) # mother father
    


# Verfügbare I2C-Geräte scannen
print("I2C Geräte:", i2c.scan())

tof = VL53L0X(i2c)



while True:
    
    tof.start()
    distance = tof.read()
    tof.stop()
    
    #sensor_data = "Temp: 24.5°C, Humidity: 60%"  # Beispiel-Daten
    sensor_data = distance  # Beispiel-Daten
    print(type(distance)) 
    print(f"Daten gesendet: {sensor_data}")
    time.sleep(1)





    
    
    
