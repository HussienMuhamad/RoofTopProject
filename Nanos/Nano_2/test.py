import time
import network
import socket
import ujson
import machine
import gc
from machine import Pin
from bodenfeuchtigkeit import Bodenfeuchtigkeit



boden_sensor = Bodenfeuchtigkeit(pin_nummer=1)  # Pin ggf. anpassen

def readSensor():
    sensorsData = {"feuchtigkeit": 0, "error": False}
    try:
        feuchte = boden_sensor.feuchtigkeit_in_prozent()
        sensorsData["feuchtigkeit"] = feuchte
    except Exception as e:
        sensorsData["error"] = True
        sensorsData["errorText"] = str(e)
        
        
    print("Sensorstatus:", sensorsData)
    time.sleep(5)
    return sensorsData



# ==== Hauptlogik ====
def main():
    
    while True:
        try:
            sensorData = readSensor()
            message = [sensorData]
            #print(message)
        except Exception as e:
            print("Fehler im Messzyklus:", e)
        #time.sleep(0.5)

# ==== Start ====
main()


