from machine import I2C, Pin, ADC
import time

class PH_Sensor:
    def __init__(self, pin):
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)  # Bereich 0-3,3V
        self.offset = 0  # Offset für Kalibrierung

    def read_voltage(self):
        raw_value = self.adc.read()
        return raw_value * 3.3 / 4095  # Rohwert in Volt umrechnen

    def calculate_ph(self, voltage):
        # Basierend auf der DFRobot-Kurve:
        return 7.0 - (2.5 - voltage) / 0.18

    def read_ph(self):
        voltage = self.read_voltage()
        ph_value = self.calculate_ph(voltage) + self.offset
        return ph_value

# Initialisieren des pH-Sensors am GPIO 34 (angepasst für M5Stack)
ph_sensor = PH_Sensor(pin=1)

# Hauptschleife
while True:
    ph_value = ph_sensor.read_ph()
    print("pH-Wert:", ph_value)
    time.sleep(1)
