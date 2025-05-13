# RPI ENV IV Example
#I2C access to the ENV IV's BMP280 and SHT40

from machine import I2C, Pin
import bmp280
from micropython_sht4x import sht4x
import time

i2c = I2C(1, sda=Pin(2), scl=Pin(3), freq=100000)
sht = sht4x.SHT4X(i2c)
bmp = bmp280.BMP280(i2c)
bmp.oversample(bmp280.BMP280_OS_HIGH)


while True:
    bmp.use_case(bmp280.BMP280_CASE_WEATHER)
    temperature, relative_humidity = sht.measurements
    print(f"SHT40 Temperature: {temperature:.2f}°C")
    print(f"SHT40 Relative Humidity: {relative_humidity:.2%}%")
    print("")
    print("BMP280 tempC: {}".format(bmp.temperature))
    print("BMP280 pressure: {}Pa".format(bmp.pressure))
    print("")
    time.sleep(0.5)