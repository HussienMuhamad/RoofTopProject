
import network
import socket
import time

import gc
gc.collect

print("WLAN Reset gestartet...")

# STA (Client-Modus) deaktivieren und zurücksetzen
sta = network.WLAN(network.STA_IF)
sta.active(True)
time.sleep(1)
sta.disconnect()
sta.active(False)
time.sleep(1)
print("Station deaktiviert.")

# AP (Access Point) deaktivieren, falls aktiv
ap = network.WLAN(network.AP_IF)
ap.active(True)
time.sleep(1)
ap.active(False)
time.sleep(1)
print("Access Point deaktiviert.")

print("Aktive Interfaces:")
print("STA aktiv:", sta.active(), " - verbunden:", sta.isconnected())
print("AP aktiv:", ap.active())


ap = network.WLAN(network.AP_IF)
ap.config(essid="nasermemar", password="87654321", authmode=network.AUTH_WPA2_PSK)
ap.active(True)
time.sleep(1)
ip = ap.ifconfig()[0]
print("📡 Access Point aktiv – IP:", ip)

UDP_PORT = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', UDP_PORT))
print("🛠 Lausche auf Port", UDP_PORT)

while True:
    data, addr = sock.recvfrom(1024)
    msg = data.decode()
    print(f"📥 Von {addr[0]}: {msg}")
    if msg == "ping":
        sock.sendto(b"pong", addr)
