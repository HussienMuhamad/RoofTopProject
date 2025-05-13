
import network
import time

SSID = "HSBO_Technik"
PASSWORD = "NRvxgykThGNX"

print("🔄 WLAN Reset wird durchgeführt...")

sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()
sta.active(False)
time.sleep(1)

sta.active(True)
print("📡 Versuche Verbindung mit Netzwerk:", SSID)
sta.connect(SSID, PASSWORD)

timeout = 15
while not sta.isconnected() and timeout > 0:
    print("⏳ Warte auf Verbindung...")
    time.sleep(1)
    timeout -= 1

if sta.isconnected():
    print("✅ Verbunden! IP-Adresse:", sta.ifconfig()[0])
else:
    print("❌ Verbindung fehlgeschlagen.")
