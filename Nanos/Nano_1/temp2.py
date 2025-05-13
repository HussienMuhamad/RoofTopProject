import network
import time

# WLAN aktivieren und resetten
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()
time.sleep(1)

SSID = "HSBO_ppsk"
PASSWORD = "NRvxgykThGNX"

print(f"Verbinde mit {SSID}...")
sta.connect(SSID, PASSWORD)

# Warten auf Verbindung
for i in range(15):
    if sta.isconnected():
        break
    print(".", end="")
    time.sleep(1)

print()
if sta.isconnected():
    print("✅ Verbunden!")
    print("IP:", sta.ifconfig()[0])
else:
    print("❌ Verbindung fehlgeschlagen.")
    print("Status:", sta.status())  # Gibt Statuscode zurück
    print("Is connected:", sta.isconnected())

    
    
    

