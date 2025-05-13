from machine import ADC, Pin
import time

class Bodenfeuchtigkeit:
    def __init__(self, pin_nummer, trocken_wert=3380, feucht_wert=2400):
        self.sensor = ADC(Pin(pin_nummer))
        self.sensor.atten(ADC.ATTN_11DB)  # Bereich 0 - 3.3V
        
        # Feste Kalibrierungswerte
        self.trocken_wert = trocken_wert  # Luft (trocken)
        self.feucht_wert = feucht_wert    # Wasser (feucht)

    def lese_wert(self):
        """Liest den aktuellen Feuchtigkeitswert"""
        return self.sensor.read()

    def feuchtigkeit_in_prozent(self):
        """Berechnet die Feuchtigkeit als Prozentwert (umgekehrt)"""
        wert = self.lese_wert()
        
        # Neue Formel: Umgekehrte Berechnung
        prozent = (self.trocken_wert - wert) / (self.trocken_wert - self.feucht_wert) * 100
        # Begrenzung zwischen 0 % und 100 %
        prozent = max(0, min(100, prozent))
        
        return prozent

    def feuchtigkeitsstatus(self):
        """Gibt den Status der Bodenfeuchtigkeit zurück"""
        wert = self.lese_wert()
        schwelle_trocken = self.trocken_wert - ((self.trocken_wert - self.feucht_wert) * 0.3)
        schwelle_feucht = self.feucht_wert + ((self.trocken_wert - self.feucht_wert) * 0.3)

        prozent = self.feuchtigkeit_in_prozent()  # Berechne den Prozentwert

        if prozent <= 30:
            return f"Feuchtigkeitswert: {wert} | Feuchtigkeit: {prozent:.2f}% | Erde ist trocken! Gießen notwendig."
        elif prozent >= 70:
            return f"Feuchtigkeitswert: {wert} | Feuchtigkeit: {prozent:.2f}% | Erde ist feucht. Kein Gießen notwendig."
        else:
            return f"Feuchtigkeitswert: {wert} | Feuchtigkeit: {prozent:.2f}% | Erde ist leicht feucht."

    def überwache_sensor(self, intervall=2):
        """Dauerhafte Überwachung des Sensors"""
        while True:
            print(self.feuchtigkeitsstatus())
            time.sleep(intervall)
