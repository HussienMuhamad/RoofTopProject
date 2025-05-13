from vl53l0x import VL53L0X
from machine import SoftI2C
from machine import Pin
import time
import machine

machine.freq(80000000)
print("freq: ", machine.freq())
time.sleep(1)

i2c = SoftI2C(scl=Pin(1), sda=Pin(2))
time.sleep(1)

busAdresse = i2c.scan()
print("BusAdresse:",busAdresse)

while True:
    if 0x29 in i2c.scan():
        sensorsData = {"distance":0}
        tof = VL53L0X(i2c)
        tof.start()
        sensorsData["distance"] = tof.read()
        print(sensorsData)
        tof.stop()
        time.sleep(1)
    else:
        print("no sensore")
