import network
import time

class WifiControl:
    
    def __init__(self, stationSsid="Core2_AP", stationPassword="12345678"):
        self.stationSsid = stationSsid
        self.stationPassword = stationPassword

        # Station-Interface anlegen (ausgeschaltet)
        self.staIf = network.WLAN(network.STA_IF)
        self.staIf.active(False)
        time.sleep(2)

    def resetWifi(self):
        print("Starte WLAN-Reset...")
        # Erst checken, ob aktiv
        if self.staIf.active():
            try:
                self.staIf.disconnect()
            except OSError as e:
                print("Fehler bei disconnect (ignoriere):", e)
            time.sleep(0.5)  # kleine Pause

            self.staIf.active(False)
            time.sleep(0.5)  # kurze Wartezeit
        else:
            print("STA war gar nicht aktiv, setze es nur auf inactive.")

        # Danach neu aktivieren
        self.staIf.active(True)
        time.sleep(1)  # dem Treiber Zeit geben
        print("Reset abgeschlossen, STA-Interface neu aktiv.")


    def connectStation(self):
        """
        Baut Verbindung mit self.stationSsid / self.stationPassword auf,
        falls nicht bereits verbunden.
        Fängt 'Wifi Internal Error' ab, damit das Programm nicht crasht.
        """
        if not self.staIf.isconnected():
            print(f"Versuche WLAN-Verbindung mit: {self.stationSsid}")
            try:
                self.staIf.connect(self.stationSsid, self.stationPassword)
            except OSError as e:
                print("Fehler in connectStation (nicht fatal):", e)
                # Du kannst hier z.B. ein Kurz-Warten oder Re-Init versuchen
                # oder einfach return, damit der async Task später neu versucht.
                time.sleep(2)
                return



    def isConnected(self):
        return self.staIf.isconnected()

    def getIpAddress(self):
        if self.staIf.isconnected():
            return self.staIf.ifconfig()[0]
        return None
