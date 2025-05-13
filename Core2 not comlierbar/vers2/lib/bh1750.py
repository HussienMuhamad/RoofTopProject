# bh1750.py
# MicroPython-Treiber für den BH1750 Lichtsensor
# Getestet mit BH1750FVI-Datenblatt, I2C-Schnittstelle

import time

class BH1750:
    """
    Klasse zur Ansteuerung des BH1750-Lichtsensors über I2C.
    Standard-Adresse ist 0x23 (ADDR-Pin auf GND).
    Falls ADDR-Pin auf VCC liegt, lautet die Adresse 0x5C (in manchen Datenblättern 0x5C oder 0x5B).
    """

    # Mögliche Befehle gemäß BH1750FVI-Datenblatt:
    POWER_DOWN                = 0x00
    POWER_ON                  = 0x01
    RESET                     = 0x07
    
    # Kontinuierliche Modi:
    CONT_H_RES_MODE          = 0x10  # 1 lx Auflösung, ~120ms
    CONT_H_RES_MODE2         = 0x11  # 0.5 lx Auflösung, ~120ms
    CONT_L_RES_MODE          = 0x13  # 4 lx Auflösung, ~16ms
    
    # Einmalige Modi (nach Messung geht Sensor in POWER_DOWN):
    ONE_TIME_H_RES_MODE      = 0x20  # 1 lx Auflösung, ~120ms
    ONE_TIME_H_RES_MODE2     = 0x21  # 0.5 lx Auflösung, ~120ms
    ONE_TIME_L_RES_MODE      = 0x23  # 4 lx Auflösung, ~16ms

    def __init__(self, i2c, address=0x23):
        """
        :param i2c: I2C-Objekt (z. B. machine.SoftI2C oder machine.I2C).
        :param address: I2C-Adresse des BH1750 (0x23 oder 0x5C).
        """
        self.i2c = i2c
        self.address = address

    def _write_cmd(self, cmd):
        """ Sendet ein einzelnes Byte (Command) an den BH1750. """
        self.i2c.writeto(self.address, bytes([cmd]))

    def powerOn(self):
        """ Sensor einschalten (POWER_ON). """
        self._write_cmd(self.POWER_ON)

    def powerDown(self):
        """ Sensor ausschalten (POWER_DOWN). """
        self._write_cmd(self.POWER_DOWN)

    def reset(self):
        """
        Reset des Daten-Registers.
        Nur gültig, wenn der Sensor zuvor mit POWER_ON eingeschaltet wurde.
        """
        self._write_cmd(self.RESET)

    def readLightOnce(self, mode=ONE_TIME_H_RES_MODE):
        """
        Führt eine Einzelmessung im angegebenen Modus durch.
        Der Sensor geht nach Messung automatisch in POWER_DOWN.
        
        :param mode: z. B. BH1750.ONE_TIME_H_RES_MODE (Standard).
        :return: float - gemessene Helligkeit in Lux.
        """
        # Befehl senden
        self._write_cmd(mode)
        
        # Laut Datenblatt max. ~180 ms Wartezeit bei H-Resolution
        # Wir setzen hier 180 ms, um sicher das Ergebnis zu haben.
        if mode in [self.ONE_TIME_H_RES_MODE, self.ONE_TIME_H_RES_MODE2]:
            time.sleep_ms(180)
        else:
            time.sleep_ms(24)  # z. B. L-Resolution

        # 2 Bytes vom Sensor lesen
        data = self.i2c.readfrom(self.address, 2)
        raw = (data[0] << 8) | data[1]

        # Konvertierung laut Datenblatt: Wert / 1.2 = Lux
        # (Gilt für H-Resolution (1 lx/count). Bei L-Res wird's etwas anders,
        #  das Datenblatt sieht jedoch dieselbe Formel vor, nur ist die Auflösung 4 lx/count.)
        lux = raw / 1.2
        return lux

    def readForDuration(self, durationSeconds, interval=0.05):
        """
        Führt wiederholt Einzelmessungen (One-Time-High-Res) im angegebenen Zeitraum aus
        und liefert den Mittelwert (oder letzten Messwert) zurück.
        
        :param durationSeconds: Gesamtzeit der Messung.
        :param interval: Pause zwischen den Einzelmessungen (Sekunden).
        :return: float - gemittelte Helligkeit in Lux im Zeitraum.
        """
        start = time.time()
        values = []
        while (time.time() - start) < durationSeconds:
            val = self.readLightOnce(self.ONE_TIME_H_RES_MODE)
            values.append(val)
            time.sleep(interval)
        
        if not values:
            return 0.0
        return sum(values) / len(values)

    def continuousModeStart(self, mode=CONT_H_RES_MODE):
        """
        Startet den kontinuierlichen Messmodus. Sensor bleibt in POWER_ON, misst permanent.
        
        :param mode: z. B. BH1750.CONT_H_RES_MODE
        :return: None
        """
        self.powerOn()       # erst einschalten
        self._write_cmd(mode)  # kont. Messmodus setzen

    def continuousModeRead(self):
        """
        Liest den zuletzt verfügbaren Messwert aus, ohne den Modus zu beenden.
        (gilt nur, wenn continuousModeStart(...) aufgerufen wurde)
        
        :return: float - Helligkeit in Lux
        """
        data = self.i2c.readfrom(self.address, 2)
        raw = (data[0] << 8) | data[1]
        lux = raw / 1.2
        return lux
