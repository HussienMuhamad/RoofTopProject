from machine import ADC, Pin
import time

class Bodenfeuchtigkeit:
    def __init__(self, pin_nummer, trocken_wert=3500, feucht_wert=2400):
        self.sensor = ADC(Pin(pin_nummer))
        self.sensor.atten(ADC.ATTN_11DB)  # Bereich 0 - 3.3V
        
        # Feste Kalibrierungswerte
        self.trocken_wert = trocken_wert  # Luft (trocken)
        self.feucht_wert = feucht_wert    # Wasser (feucht)

    def lese_wert(self):
        """Liest den aktuellen Feuchtigkeitswert"""
        return self.sensor.read()

    def feuchtigkeitsstatus(self):
        """Gibt den Status der Bodenfeuchtigkeit zurück"""
        wert = self.lese_wert()
        schwelle_trocken = self.trocken_wert - ((self.trocken_wert - self.feucht_wert) * 0.3)
        schwelle_feucht = self.feucht_wert + ((self.trocken_wert - self.feucht_wert) * 0.3)

        if wert >= schwelle_trocken:
            return f"Feuchtigkeitswert: {wert} | Erde ist trocken! Gießen notwendig."
        elif wert <= schwelle_feucht:
            return f"Feuchtigkeitswert: {wert} | Erde ist feucht. Kein Gießen notwendig."
        else:
            return f"Feuchtigkeitswert: {wert} | Erde ist leicht feucht."

    def überwache_sensor(self, intervall=2):
        """Dauerhafte Überwachung des Sensors"""
        while True:
            print(self.feuchtigkeitsstatus())
            time.sleep(intervall)
