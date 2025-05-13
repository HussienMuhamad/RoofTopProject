from sht40   import SHT40
from bmp280  import BMP280
from vl53l0x import VL53L0X
from bh1750  import BH1750


from machine import Pin
from machine import SoftI2C
import time


class SensorControl():
    
    
    def __init__(self, i2c, sensorAddresses):
        self.i2c = i2c
        self.sensorAddList = sensorAddresses
        self.sensorsData = {"TempSht40":0, "HumidSht40":0, "TempBmp":0, "PressBmp":0, "LightIntens":0, "dist":0}
    
    def findSensorPort(self, sensorAdd):
        port = -1
        for i in range(len(self.sensorAddList)):
            for j in range(len(self.sensorAddList[i])):
                if self.sensorAddList[i][j] == sensorAdd:
                    port = i # if adress couldnt be found ????
        return port
    
    def readTempHum(self):
        port = self.findSensorPort(0x44)
        print(f"sht at port: {port}")
        self.i2c.writeto(0x70, bytearray([1 << port]))
        time.sleep(0.05)
        self.i2c.writeto(0x44, b'\xFD')
        time.sleep(0.05)
        data = self.i2c.readfrom(0x44, 6)
         # Temperatur berechnen (siehe Datenblatt des SHT40)
        temp_raw = data[0] << 8 | data[1]
        temperature = -45 + (175 * temp_raw / 65535.0)
        # Luftfeuchtigkeit berechnen
        humidity_raw = data[3] << 8 | data[4]
        humidity = 100 * humidity_raw / 65535.0
        self.i2c.writeto(0x70, bytearray([0x00]))
        return temperature, humidity
    

    def readTempPress(self):
        port = self.findSensorPort(0x76)
        print(f"bmp at port: {port}")
        self.i2c.writeto(0x70, bytearray([1 << port]))
        time.sleep(0.05)
        bmp   = BMP280(self.i2c)
        temp  = bmp.temperature
        press = bmp.pressure
        self.i2c.writeto(0x70, bytearray([0x00]))
        return temp, press
    
    def readDistance(self, repead=10):
        port = self.findSensorPort(0x29)
        print(f"ToF at port: {port}")
        self.i2c.writeto(0x70, bytearray([1 << port]))
        time.sleep(0.05)
        tof = VL53L0X(self.i2c)
        distance = 0
        print("Distanz wird gelesen...")
        tof.start()
        distance = tof.read()
        tof.stop
        self.i2c.writeto(0x70, bytearray([0x00]))
        return distance
    
    def readLight(self, durationSeconds):
        port = self.findSensorPort(0x23)  # BH1750 Lichtsensor
        
        self.i2c.writeto(0x70, bytearray([1 << port]))  # Sicherer Shift
        time.sleep(0.05)

        dlight = BH1750(self.i2c)
        light = dlight.readForDuration(durationSeconds, interval=0.05)

        self.i2c.writeto(0x70, bytearray([0x00]))  # Multiplexer zurücksetzen
        return light

        
    
    def getSensorsData(self):
       sht40Data = self.readTempHum()
       self.sensorsData["TempSht40"]  = sht40Data[0]
       self.sensorsData["HumidSht40"] = sht40Data[1]
       
       bmpData = self.readTempPress()
       self.sensorsData["TempBmp"]  = bmpData[0]
       self.sensorsData["PressBmp"] = bmpData[1]
       
       self.sensorsData["LightIntens"] = self.readLight(2)
       
       #self.sensorsData["dist"] = self.readDistance(10)
       
       return self.sensorsData
       
       

        
        


        

