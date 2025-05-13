
import network
import socket
import time
import ujson
import machine
from machine import Pin
from machine import SoftI2C

import gc
gc.collect()

machine.freq(80000000)
print("freq: ", machine.freq())

from vl53l0x import VL53L0X


# ==== Konfiguration ====
SSID = "nasermemar"
PASSWORD = "87654321"
UDP_IP = "192.168.4.1"
UDP_PORT = 12345
SENSOR_TAG = "TOF"
LED_PIN = 7
WAKE_DURATION_SEC = 14             # ca. 2 Messungen alle 10s
SLEEP_DURATION_MS = 30 * 1000      # 30 Sekunden schlafen

# ==== Setup ====
led = Pin(LED_PIN, Pin.OUT)
i2c = SoftI2C(scl=Pin(1), sda=Pin(2))

# ==== 1. WLAN Reset ====
def resetWifi():

    # STA zurücksetzen
    sta = network.WLAN(network.STA_IF)
    sta.active(True), time.sleep(1)
    sta.disconnect()
    sta.active(False), time.sleep(1)
    print("Station wurde zurückgesetzt!")

    # AP deaktivieren
    ap = network.WLAN(network.AP_IF)
    ap.active(True), time.sleep(1)
    ap.active(False), time.sleep(1)
    print("Access Point wurde zurückgesetzt!")

    print("Status:")
    print("STA aktiv:", sta.active(), " - verbunden:", sta.isconnected())
    print("AP aktiv:", ap.active())

# ==== 2. WLAN Verbindung ====
def connectWifi(timeout=120):
    sta = network.WLAN(network.STA_IF)
    sta.active(True), time.sleep(1)
    print("Verbindung mit Core2 wird aufgebaut...")
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
    print("Verbunden mit AP! -> IP:", sta.ifconfig()[0])
    return sta

# ==== 3. Sensorwert holen (Platzhalter) ====
def readSensor():
    sensorsData = {"distance": 0, "error": False}
    try:
        devices = i2c.scan()
        if 0x29 in devices:
            tof = VL53L0X(i2c)
            tof.start()
            dist = tof.read()
            tof.stop()
            time.sleep(1)
            sensorsData["distance"] = dist
        else:
            sensorsData["error"] = True # "VL53L0X not found"
    except Exception as e:
        sensorsData["error"] = True
        sensorsData["errorText"] = str(e)

    print("Sensorstatus:", sensorsData)
    time.sleep(5)
    return sensorsData


# ==== 4. Daten senden ====
def sendData(payload):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(payload.encode(), (UDP_IP, UDP_PORT))
        print("Gesendet:", payload)
    except Exception as e:
        print("Fehler beim Senden:", e)

# ==== 5. Schlafmodus ====
def go2Sleep():
    print("Gehe in Deep Sleep für 1 Stunde...")
    led.off()
    machine.deepsleep(SLEEP_DURATION_MS)

# ==== 6. Hauptlogik ====
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

main()


