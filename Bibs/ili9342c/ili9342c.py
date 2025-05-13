import time
from machine import Pin, SPI

# Konstanten aus ili9342c.h (oder ggf. abgewandelt):
ILI9342C_SWRESET = 0x01
ILI9342C_SLPIN   = 0x10
ILI9342C_SLPOUT  = 0x11
ILI9342C_INVOFF  = 0x20
ILI9342C_INVON   = 0x21
ILI9342C_DISPOFF = 0x28
ILI9342C_DISPON  = 0x29
ILI9342C_CASET   = 0x2A
ILI9342C_PASET   = 0x2B
ILI9342C_RAMWR   = 0x2C
ILI9342C_RAMRD   = 0x2E
# ... ggf. weitere Befehle ...

# Beispiel-Farbwerte
BLACK   = 0x0000
WHITE   = 0xFFFF
RED     = 0xF800
GREEN   = 0x07E0
BLUE    = 0x001F
YELLOW  = 0xFFE0
CYAN    = 0x07FF
MAGENTA = 0xF81F

class ILI9342C:
    def __init__(self, spi_id=1, baudrate=40000000,
                 pin_dc=2, pin_cs=15, pin_reset=4,
                 width=320, height=240):
        """
        Vereinfachtes Beispiel zur Initialisierung:
          spi_id:  ID oder Objekt der SPI-Schnittstelle (z.B. 1)
          baudrate: SPI-Taktfrequenz
          pin_dc, pin_cs, pin_reset: GPIO-Pins für Data/Command, Chip Select, Reset
          width, height: Auflösung
        """
        # Display-Größe
        self.width  = width
        self.height = height

        # SPI konfigurieren
        self.spi = SPI(
            spi_id,
            baudrate=baudrate,
            polarity=0,
            phase=0
        )

        # Pins konfigurieren
        self._dc     = Pin(pin_dc, Pin.OUT)
        self._cs     = Pin(pin_cs, Pin.OUT)
        self._reset  = Pin(pin_reset, Pin.OUT)

        # Pins standardmäßig "high" setzen
        self._dc.value(1)
        self._cs.value(1)
        self._reset.value(1)

        # Hardware-Reset während Init
        self.hard_reset()

        # Kurze Wartezeit
        time.sleep_ms(100)

        # Aus Sleep aufwachen
        self.sleep_mode(False)
        time.sleep_ms(120)

        # Software-Reset
        self.soft_reset()
        time.sleep_ms(120)

        # Display einschalten
        self.write_cmd(ILI9342C_DISPON)
        time.sleep_ms(120)

        # (Weitere Initialisierungsschritte / Gamma / Pixel-Format usw. hier einfügen)

    # --------------------------------------------------------
    # Niedrig-Level-Funktionen
    # --------------------------------------------------------
    def write_cmd(self, cmd, data=None):
        """Sende ein Command (cmd) und optional ein Bytearray data an das Display."""
        self._cs.value(0)
        # DC = 0 => Command
        self._dc.value(0)
        # Ein Byte für das Kommando
        self.spi.write(bytearray([cmd]))

        if data is not None:
            # DC = 1 => Daten
            self._dc.value(1)
            if isinstance(data, int):
                # Falls nur 1 Byte
                self.spi.write(bytearray([data]))
            else:
                # Falls Bytearray
                self.spi.write(data)

        self._cs.value(1)

    def set_address_window(self, x0, y0, x1, y1):
        """
        Definiert den Ausgabebereich im GRAM (Memory Window).
        x0, y0, x1, y1 sind die Eckkoordinaten des Rechtecks.
        """
        # Column Address Set (CASET)
        self.write_cmd(ILI9342C_CASET, bytearray([
            (x0 >> 8) & 0xFF,
            x0 & 0xFF,
            (x1 >> 8) & 0xFF,
            x1 & 0xFF
        ]))

        # Page Address Set (PASET)
        self.write_cmd(ILI9342C_PASET, bytearray([
            (y0 >> 8) & 0xFF,
            y0 & 0xFF,
            (y1 >> 8) & 0xFF,
            y1 & 0xFF
        ]))

        # RAMWR => ab jetzt Pixeldaten
        self.write_cmd(ILI9342C_RAMWR)

    # --------------------------------------------------------
    # Basis-Funktionen wie Reset, Sleep, Inversion
    # --------------------------------------------------------
    def hard_reset(self):
        """Zieht den Hardware-Reset-Pin kurz auf 0."""
        self._reset.value(1)
        time.sleep_ms(5)
        self._reset.value(0)
        time.sleep_ms(20)
        self._reset.value(1)
        time.sleep_ms(20)

    def soft_reset(self):
        """Software-Reset via Befehl SWRESET."""
        self.write_cmd(ILI9342C_SWRESET)

    def sleep_mode(self, enable=True):
        """
        Schaltet den Sleep-Modus ein (True => 0x10) oder aus (False => 0x11).
        """
        if enable:
            self.write_cmd(ILI9342C_SLPIN)
        else:
            self.write_cmd(ILI9342C_SLPOUT)

    def inversion_mode(self, enable=False):
        """Display-Inversion an/aus."""
        if enable:
            self.write_cmd(ILI9342C_INVON)
        else:
            self.write_cmd(ILI9342C_INVOFF)

    # --------------------------------------------------------
    # Zeichenfunktionen
    # --------------------------------------------------------
    def fill_rect(self, x, y, w, h, color):
        """Füllt das Rechteck (x, y, w, h) mit color (16-Bit RGB565)."""
        if (x + w - 1) >= self.width or (y + h - 1) >= self.height:
            # Grenzen anpassen (einfacher Clip)
            w = min(w, self.width - x)
            h = min(h, self.height - y)

        # Fenster setzen
        self.set_address_window(x, y, x + w - 1, y + h - 1)

        # Jetzt Pixelwerte senden
        # Jedes Pixel: 2 Byte (High, Low)
        hi = (color >> 8) & 0xFF
        lo = color & 0xFF
        # Ein Rechteck aus w*h Pixeln
        pixel_count = w * h

        # Maximaler Chunk, um Speicher zu sparen:
        chunk_size = 1024
        # Bytearray vorbereiten, z.B. 1024*2 = 2048 Bytes
        buf = bytearray(chunk_size * 2)
        for i in range(chunk_size):
            buf[2*i]   = hi
            buf[2*i+1] = lo

        self._cs.value(0)
        self._dc.value(1)  # Datenmodus
        # So lange Blöcke schicken, bis pixel_count = 0
        while pixel_count > 0:
            block = min(pixel_count, chunk_size)
            self.spi.write(buf[:block*2])
            pixel_count -= block

        self._cs.value(1)

    def draw_pixel(self, x, y, color):
        """Setzt genau 1 Pixel in der Farbe color."""
        if x >= self.width or y >= self.height:
            return
        self.set_address_window(x, y, x, y)
        hi = (color >> 8) & 0xFF
        lo = color & 0xFF
        self._cs.value(0)
        self._dc.value(1)
        self.spi.write(bytearray([hi, lo]))
        self._cs.value(1)

    # --------------------------------------------------------
    # usw... weitere Methoden (Scrolling, Lesen, Grafikprimitive, Textausgabe etc.)
    # --------------------------------------------------------

if __name__ == "__main__":
    # Beispiel, wie man diese Klasse nutzen könnte

    # Display-Objekt erzeugen
    display = ILI9342C(
        spi_id=1,       # Ihr SPI-Bus
        baudrate=40000000,
        pin_dc=2,
        pin_cs=15,
        pin_reset=4,
        width=320,
        height=240
    )

    # Display: Hintergrund Schwarz
    display.fill_rect(0, 0, display.width, display.height, BLACK)

    # Kleines weißes Rechteck
    display.fill_rect(50, 50, 100, 60, WHITE)

    # Einzelne Pixel in Gelb
    display.draw_pixel(10, 10, YELLOW)
    display.draw_pixel(11, 11, YELLOW)

    # Kurz warten
    time.sleep(2)

    # Display ausschalten (DISPOFF)
    display.write_cmd(ILI9342C_DISPOFF)
    # Und ggf. Sleep-Modus an
    display.sleep_mode(True)
    print("Display in Sleep versetzt!")
