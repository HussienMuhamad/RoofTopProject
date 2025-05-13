import sys
import os
sys.path.append('/usocketio')
sys.path.append('/uwebsockets')

from machine import Pin
import time
import json
import network
from bodenfeuchtigkeit import Bodenfeuchtigkeit  # Import der Bodenfeuchtigkeit-Klasse
from websocket_client import WebSocketClient  # Import der WebSocket-Client-Klasse



from transport import SocketIO

# Client-Funktion zum Senden von Daten
def send_sensor_data(uri):
    with SocketIO(uri) as client:
        while True:
            sensor_data = {
                "temperature": 24.5,  # Beispielwert
                "humidity": 60       # Beispielwert
            }
            client.emit("sensor_data", sensor_data)
            print("Sent data:", sensor_data)
            time.sleep(5)  # Daten alle 5 Sekunden senden

# Hauptprogramm
if __name__ == "__main__":
    uri = "ws://192.168.1.100:8080"  # IP/Port des Servers
    send_sensor_data(uri)
