import time
import network
import socket
import ujson
import machine
import gc
from machine import Pin
from bodenfeuchtigkeit import Bodenfeuchtigkeit

# ==== System Setup ====
gc.collect()
machine.freq(80000000)
print("freq:", machine.freq())

# ==== Konfiguration ====
SSID = "nasermemar"
PASSWORD = "87654321"
UDP_IP = "192.168.4.1"
UDP_PORT = 12345
SENSOR_TAG = "FEUCHTIGKEIT BETT 1"
LED_PIN = 7
WAKE_DURATION_SEC = 14
SLEEP_DURATION_MS = 30 * 1000

# ==== LED Setup ====
led = Pin(LED_PIN, Pin.OUT)

# ==== WLAN Reset ====
def resetWifi():
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    time.sleep(1)
    sta.disconnect()
    sta.active(False)
    time.sleep(1)
    print("WLAN zurückgesetzt.")

    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    time.sleep(1)
    ap.active(False)
    time.sleep(1)
    print("Access Point zurückgesetzt.")

# ==== WLAN verbinden ====
def connectWifi(timeout=120):
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    time.sleep(1)
    print("Verbinde mit WLAN...")
    sta.connect(SSID, PASSWORD)

    start = time.time()
    while not sta.isconnected():
        if time.time() - start > timeout:
            print("WLAN-Verbindung fehlgeschlagen.")
            machine.deepsleep(SLEEP_DURATION_MS)
        led.on()
        time.sleep(0.1)
        led.off()
        time.sleep(0.5)

    led.on()
    print("Verbunden! IP:", sta.ifconfig()[0])
    return sta

# ==== Bodenfeuchtigkeitssensor vorbereiten ====
boden_sensor = Bodenfeuchtigkeit(pin_nummer=1)  # Pin ggf. anpassen

# ==== Sensorwert lesen ====
def readSensor():
    sensorsData = {"feuchtigkeit": 0, "error": False}
    try:
        feuchte = boden_sensor.feuchtigkeit_in_prozent()
        sensorsData["feuchtigkeit"] = feuchte
    except Exception as e:
        sensorsData["error"] = True
        sensorsData["errorText"] = str(e)
        
    #if not sensorsData["error"]:
    #   print(f"Feuchtigkeit: {sensorsData['feuchtigkeit']:.2f}%")
        
    print("Sensorstatus:", sensorsData)
    time.sleep(5)
    return sensorsData

# ==== UDP senden ====
def sendData(payload):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(payload.encode(), (UDP_IP, UDP_PORT))
        print("Gesendet:", payload)
    except Exception as e:
        print("Fehler beim Senden:", e)

# ==== Deep Sleep ====
def go2Sleep():
    print("Gehe in Deep Sleep für 30 Sekunden...")
    led.off()
    machine.deepsleep(SLEEP_DURATION_MS)

# ==== Hauptlogik ====
def main():
    resetWifi()
    wlan = connectWifi()
    if not wlan:
        go2Sleep()
        return

    startTime = time.time()
    while time.time() - startTime < WAKE_DURATION_SEC:
        try:
            now = time.localtime()
            timestamp = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(*now[:6])
            sensorData = readSensor()
            message = [SENSOR_TAG, timestamp, sensorData]
            payload = ujson.dumps(message)
            sendData(payload)
        except Exception as e:
            print("Fehler im Messzyklus:", e)
        time.sleep(1)

    go2Sleep()

# ==== Start ====
main()


