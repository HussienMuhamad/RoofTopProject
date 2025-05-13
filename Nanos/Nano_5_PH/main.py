from machine import Pin, ADC
import network
import socket
import time
import ujson
import machine
import gc

# ==== Grundeinstellungen ====
gc.collect()
machine.freq(80000000)
print("CPU-Frequenz:", machine.freq())

# ==== Konfiguration ====
SSID = "nasermemar"
PASSWORD = "87654321"
UDP_IP = "192.168.4.1"
UDP_PORT = 12345
SENSOR_TAG = "PH"
LED_PIN = 7

# ==== Initialisierung ====
led = Pin(LED_PIN, Pin.OUT)
ph_signal = ADC(Pin(1))
ph_signal.atten(ADC.ATTN_11DB)

# ==== Kalibrierung ====
calibration_slope = 16.57
calibration_offset = -19.51

# ==== pH-Sensor Funktionen ====
def calculate_ph_with_calibration(voltage):
    return calibration_slope * voltage + calibration_offset

def read_voltage():
    raw_value = ph_signal.read()
    voltage = raw_value * 3.3 / 4095
    return voltage

def readSensor():
    sensorsData = {"ph": 0, "error": False}
    try:
        voltage = read_voltage()
        ph_value = calculate_ph_with_calibration(voltage)
        sensorsData["ph"] = round(ph_value, 2)
        print(f"Spannung: {voltage:.2f} V | pH-Wert: {ph_value:.2f}")
    except Exception as e:
        sensorsData["error"] = True
        sensorsData["errorText"] = str(e)
        print("Fehler beim pH-Sensor:", sensorsData["errorText"])
    return sensorsData

# ==== WLAN zurücksetzen ====
def resetWifi():
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    time.sleep(1)
    sta.disconnect()
    sta.active(False)
    time.sleep(1)

    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    time.sleep(1)
    ap.active(False)
    time.sleep(1)

    print("WLAN zurückgesetzt.")

# ==== WLAN verbinden ====
def connectWifi(timeout=30):
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    time.sleep(1)
    print("Verbinde mit WLAN...")
    sta.connect(SSID, PASSWORD)

    start = time.time()
    while not sta.isconnected():
        if time.time() - start > timeout:
            print("WLAN-Verbindung fehlgeschlagen.")
            return None
        led.on()
        time.sleep(0.1)
        led.off()
        time.sleep(0.3)

    led.on()
    print("Verbunden! IP:", sta.ifconfig()[0])
    return sta

# ==== Daten senden ====
def sendData(payload):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(payload.encode(), (UDP_IP, UDP_PORT))
        print("Gesendet:", payload)
    except Exception as e:
        print("Fehler beim Senden:", e)

# ==== Hauptlogik ====
def main():
    resetWifi()
    wlan = connectWifi()
    if not wlan:
        return

    print("Starte Messzyklus...")
    try:
        while True:
            now = time.localtime()
            timestamp = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(*now[:6])
            sensorData = readSensor()
            message = [SENSOR_TAG, timestamp, sensorData]
            payload = ujson.dumps(message)
            sendData(payload)

            time.sleep(1)  # alle 10 Sekunden messen & senden

    except KeyboardInterrupt:
        print("Messung manuell abgebrochen.")
        led.off()

main()
