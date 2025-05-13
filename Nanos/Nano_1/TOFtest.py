

import network
import socket
import time




from machine import Pin, I2C
from vl53l0x import VL53L0X

# I2C initialisieren (ersetze GPIO-Werte entsprechend deiner Hardware)
i2c = I2C(0, scl=Pin(1), sda=Pin(2))

# Verfügbare I2C-Geräte scannen
print("I2C Geräte:", i2c.scan())

tof = VL53L0X(i2c)



while True:
    
    tof.start()
    distance = tof.read()
    tof.stop()
    
    #sensor_data = "Temp: 24.5°C, Humidity: 60%"  # Beispiel-Daten
    sensor_data = distance  # Beispiel-Daten
    #print(type(distance)) 
    print(f"Daten gesendet: {sensor_data}")
    time.sleep(1)





    
    
    
