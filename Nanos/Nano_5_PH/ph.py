from machine import Pin, ADC
import time

# Initialisierung
ph_signal = ADC(Pin(1))
ph_signal.atten(ADC.ATTN_11DB)

# Vorgespeicherte Kalibrierungswerte
calibration_slope = 16.57  # Steigung aus vorheriger Kalibrierung
calibration_offset = -19.51  # Offset aus vorheriger Kalibrierung

# Funktionen
def calculate_ph_with_calibration(voltage):
    return calibration_slope * voltage + calibration_offset

def read_voltage():
    raw_value = ph_signal.read()
    voltage = raw_value * 3.3 / 4095  # Umrechnung des Rohwerts in Spannung (bei 12-Bit-ADC)
    return voltage

# Hauptprogramm
try:
    print("Starte pH-Sensor Messung mit vorgespeicherter Kalibrierung...")

    # Hauptschleife für Messungen
    while True:
        voltage = read_voltage()
        ph_value = calculate_ph_with_calibration(voltage)
        print("Spannung: {:.2f} V, pH-Wert: {:.2f}".format(voltage, ph_value))

        # Optional: Daten in eine Datei speichern
        #with open('ph_log.txt', 'a') as f:
        #    f.write("Spannung: {:.2f} V, pH-Wert: {:.2f}\n".format(voltage, ph_value))

        time.sleep(1)

except KeyboardInterrupt:
    print("Messung beendet.")

# Hinweis: Die vorgespeicherten Kalibrierungswerte basieren auf einer vorherigen Zweipunktkalibrierung und können bei Bedarf aktualisiert werden.

