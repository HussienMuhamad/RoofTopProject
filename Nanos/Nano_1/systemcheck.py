import network, time


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
time.sleep(2)  # Zeit geben


wlan.connect("Core2_AP", "12345678")

for i in range(10):
    if wlan.isconnected():
        print("Verbunden:", wlan.ifconfig())
        break
    print("Verbinde...", i)
    time.sleep(1)
else:
    print("Keine Verbindung.")
