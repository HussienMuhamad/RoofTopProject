from machine import Pin, SPI
#from machine import I2C
from machine import SoftI2C
import time

class SystemCheck():
    
    def __init__(self, i2c, TCAAddress):
        self.i2c = i2c
        self.TCAAddr = TCAAddress
        self.sensorsList = []
        print( "SystemCheck init -> ok")


    def lokateSensors(self): # angeschlossene sensoren an TCA mit port nummer lokalisieren
        for channel in range(8):
            self.i2c.writeto(self.TCAAddr, bytearray([1 << channel]))
            sensors = self.i2c.scan()
            self.sensorsList.append(sensors)
            #print(list1)
            time.sleep(0.01)
        #print(self.sensorsList)
        self.i2c.writeto(self.TCAAddr, bytearray([0x00]))
        #print(f"TCAADDR reset: {self.i2c.scan()}")
        
    def getSensListAsHexString(self):
        tempList.append([])
        for i in range(len(self.sensorsList)):
            for j in range(len(self.sensorsList[i])):
                tempList[i].append(hex(tempList[i][j]))
        return tempList
    
    
    def getSensListAsInt(self):
        return self.sensorsList
        
        
    




