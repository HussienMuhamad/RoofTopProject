

from machine import Pin, SoftI2C

import uasyncio as asyncio
import time
import json
import network
from uwebsockets.client import connect  # Import the WebSocket client


class WifiControl():
    
    
    def __init__(self):
        # WLAN Konfiguration
        self.SSID = "MemarHotspot"
        self.PASSWORD = "12334567"
        # WebSocket URL
        self.WEBSOCKET_URL = "wss://microgardening-backend-production.up.railway.app/sensor-data"  




    # WLAN-Verbindung herstellen
    def connectWifi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            print('Verbindung zu WLAN wird hergestellt...')
            wlan.connect(self.SSID, self.PASSWORD)
            while not wlan.isconnected():
                time.sleep(1)
        print('Mit WLAN verbunden, IP-Adresse:', wlan.ifconfig())

    # Hauptloop für WebSocket und Sensoren
    def sendDataViaWebSocket(self,sensorsData):

        #sensorsData = {"TempSht40":0, "HumidSht40":0, "TempBmp":0, "PressBmp":0, "LightIntens":0, "dist":0}
        data = {
            "temperature": sensorsData["TempSht40"],
            "humidity":    sensorsData["HumidSht40"],
            "pressure": sensorsData["PressBmp"],
            "distance": sensorsData["dist"],
            "Light": sensorsData["LightIntens"]
        }

        # Convert to JSON
        json_data = json.dumps(data)

        # Connect to WebSocket server
        ws = connect(self.WEBSOCKET_URL)

        try:
            # Send data via WebSocket
            ws.send(json_data)
            print("Daten gesendet:", json_data)
        except Exception as e:
            print("Fehler beim Senden von Daten:", e)
        finally:
            ws.close()


# Beispiel für die Verwendung
def main():
    controller = WifiControl()
    controller.connectWifi()

    sensorsData = {
        "TempSht40": 22.5,
        "HumidSht40": 45,
        "PressBmp": 1013,
        "dist": 30,
        "LightIntens": 500
    }

    controller.sendDataViaWebSocket(sensorsData)

if __name__ == "__main__":
    main()

