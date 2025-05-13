from machine import Pin, ADC
import time

# Initialisierung
ph_signal = ADC(Pin(1))
ph_signal.atten(ADC.ATTN_11DB)  # Bereich 0-3,3V

# Globale Kalibrierung
calibration_offset = 4.4

# Funktion zur Berechnung des pH-Wertes
def calculate_ph(voltage):
    return 7.0 - (2.5 - voltage) / 0.18  # DFRobot-Kurve

# Funktion zur Kalibrierung
def calibrate(sensor_voltage, known_ph):
    global calibration_offset
    calibration_offset = known_ph - calculate_ph(sensor_voltage)

# Hauptschleife
while True:
    # Spannung lesen
    raw_value = ph_signal.read()
    voltage = raw_value * 3.3 / 4095  # Rohwert in Volt umwandeln
    
    # pH-Wert berechnen
    ph_value = calculate_ph(voltage) + calibration_offset

    # Ausgabe in Konsole
    print("Spannung: {:.2f} V, pH-Wert: {:.2f}".format(voltage, ph_value))
    
    # Optional: Daten speichern
    with open('ph_log.txt', 'a') as f:
        f.write("Spannung: {:.2f} V, pH-Wert: {:.2f}\n".format(voltage, ph_value))
    
    time.sleep(1)
