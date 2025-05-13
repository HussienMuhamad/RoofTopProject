# ili9342cExtended.py

import time
from machine import Pin, SPI

import axp202c
from displaycontrol import DisplayControl

# ------------------------
# Wichtige ILI9342C-Befehle
# ------------------------
ILI9342C_SWRESET = 0x01   # Software Reset
ILI9342C_SLPIN   = 0x10   # Sleep In
ILI9342C_SLPOUT  = 0x11   # Sleep Out
ILI9342C_INVOFF  = 0x20   # Display Inversion OFF
ILI9342C_INVON   = 0x21   # Display Inversion ON
ILI9342C_DISPOFF = 0x28   # Display OFF
ILI9342C_DISPON  = 0x29   # Display ON
ILI9342C_CASET   = 0x2A   # Column Address Set
ILI9342C_PASET   = 0x2B   # Page Address Set
ILI9342C_RAMWR   = 0x2C   # RAM Write

class Ili9342cExtended:
    def __init__(self):
        """
        Falls du einen PMIC wie AXP192 nutzt, kannst du hier manuell 
        deine Spannungsversorgung aktivieren. Beispiel:
          axp.enablePower(axp202c.AXP192_LDO2)
        """
        # Pins für SPI und Display-Steuerung anpassen
        self.pinReset = Pin(33, Pin.OUT)
        self.pinCs    = Pin(5, Pin.OUT)
        self.pinDc    = Pin(15, Pin.OUT)

        # Standardwerte
        self.pinCs.value(1)
        self.pinDc.value(1)
        self.pinReset.value(1)

        # SPI-Schnittstelle initialisieren
        # self.spi = SPI(2,baudrate=10000000,sck=Pin(18),mosi=Pin(23)) # SPI init
        self.spi = SPI(
            2,
            baudrate=10_000_000,
            sck=Pin(18),
            mosi=Pin(23),
        )

        # Display-Reset
        self.hardwareReset()
        time.sleep_ms(50)

        # Aus dem Sleep Mode heraus
        self.writeCmd(ILI9342C_SLPOUT)
        time.sleep_ms(120)


        # Display einschalten
        self.writeCmd(ILI9342C_DISPON)
        time.sleep_ms(120)
        
        # Hier ggf. weitere Init-Kommandos
        # (Pixel-Format, Orientation usw.)

    # ---------------------------
    # Low-Level-Routinen
    # ---------------------------
    def hardwareReset(self):
        """Hardware-Reset via Reset-Pin."""
        self.pinReset.value(1)
        time.sleep_ms(5)
        self.pinReset.value(0)
        time.sleep_ms(20)
        self.pinReset.value(1)
        time.sleep_ms(20)

    def writeCmd(self, cmd, data=None):
        """
        Schickt ein 8-Bit-Kommando (cmd) + optional Daten an das Display.
        """
        # CS auf Low => selektieren
        self.pinCs.value(0)

        # DC = 0 => Kommando
        self.pinDc.value(0)
        self.spi.write(bytearray([cmd]))

        # Falls Daten vorhanden => DC=1 und Daten senden
        if data is not None:
            self.pinDc.value(1)
            if isinstance(data, int):
                self.spi.write(bytearray([data]))
            else:
                self.spi.write(data)

        # CS => High => fertig
        self.pinCs.value(1)

    # ---------------------------
    # Display an/aus
    # ---------------------------
    def displayOff(self):
        """Display OFF (0x28)."""
        self.writeCmd(ILI9342C_DISPOFF)

    def displayOn(self):
        """Display ON (0x29)."""
        self.writeCmd(ILI9342C_DISPON)

    # ---------------------------
    # Beispiel-Energiesparmethoden
    # ---------------------------
    def energyModeOn(self):
        """
        Beispiel: Display aus.
        Wenn du AXP192/202 hast, kannst du hier
        manuell DC3-Spannungen reduzieren.
        """
        print("EnergyModeOn...")
        self.displayOff()
        time.sleep_ms(1000)
        # Beispiel-Code für AXP (manuell aktivieren falls gewünscht):
        axp.setDC3Voltage(1000)
        print("Display aus.")
        return False

    def energyModeOff(self):
        """
        Beispiel: Display wieder an.
        Wenn du AXP192/202 hast, kannst du hier
        manuell DC3-Spannungen wieder erhöhen.
        """
        print("EnergyModeOff...")
        axp.setDC3Voltage(3000)
        time.sleep_ms(1000)
        self.displayOn()
        print("Display wieder an.")
        return True


axp = axp202c.PMU(address=0x34)
axp.enablePower(axp202c.AXP192_LDO2)
axp.setDC3Voltage(2700)

time.sleep(3)

display = DisplayControl(axp)
# Display ist nun initialisiert



display.energyModeOn()
# hier ggf. axp.setDC3Voltage(...) manuell einfügen, falls du AXP hast
time.sleep(3)
display.energyModeOff()
