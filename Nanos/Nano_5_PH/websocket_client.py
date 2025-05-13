import socket

class WebSocketClient:
    def __init__(self, host, port, path="/sensor-data", max_redirects=3):
        self.host = host
        self.port = port
        self.path = path
        self.sock = None
        self.max_redirects = max_redirects  # Maximale Weiterleitungen

    def connect(self):
        try:
            self._connect_to_server(self.host, self.port, self.path, 0)
        except Exception as e:
            print("Fehler bei der WebSocket-Verbindung:", e)

    def _connect_to_server(self, host, port, path, redirect_count):
        if redirect_count > self.max_redirects:
            raise Exception("Zu viele Weiterleitungen. Verbindung abgebrochen.")

        addr_info = socket.getaddrinfo(host, port)
        addr = addr_info[0][-1]
        self.sock = socket.socket()
        self.sock.connect(addr)

        # WebSocket Handshake
        handshake = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "User-Agent: MicroPythonClient/1.0\r\n"
            "\r\n"
        )

        self.sock.send(handshake.encode())
        response = self.sock.recv(1024)
        print("Handshake Response:", response)

        if b"101 Switching Protocols" in response:
            print("WebSocket verbunden.")
        elif b"301 Moved Permanently" in response:
            # Umleitung abfangen
            location = self._extract_location(response)
            if location:
                print(f"Weiterleitung zu: {location}")
                new_host, new_path = self._parse_location(location)
                self.sock.close()  # Alte Verbindung schließen
                self._connect_to_server(new_host, port, new_path, redirect_count + 1)
            else:
                raise Exception("Umleitungsziel nicht gefunden.")
        else:
            raise Exception("WebSocket-Handshake fehlgeschlagen.")

    def _extract_location(self, response):
        """ Extrahiert den Location-Header aus der Server-Antwort """
        try:
            response_str = response.decode()
            lines = response_str.split("\r\n")
            for line in lines:
                if line.lower().startswith("location:"):
                    location = line.split(":", 1)[1].strip()
                    return location
            return None
        except Exception as e:
            print("Fehler beim Extrahieren des Location-Headers:", e)
            return None

    def _parse_location(self, location):
        """ Zerlegt die URL in Host und Pfad """
        if location.startswith("wss://") or location.startswith("ws://"):
            location = location.replace("wss://", "").replace("ws://", "")
            parts = location.split("/", 1)
            host = parts[0]
            path = "/" + parts[1] if len(parts) > 1 else "/"
            return host, path
        return None, None

    def send(self, data):
        try:
            frame = self._build_frame(data)
            self.sock.send(frame)
            print("Daten gesendet:", data)
        except Exception as e:
            print("Fehler beim Senden von Daten:", e)

    def _build_frame(self, data):
        frame = b'\x81'  # FIN + Text Frame
        length = len(data)
        if length < 126:
            frame += bytes([length])
        elif length <= 0xFFFF:
            frame += b'\x7e' + length.to_bytes(2, 'big')
        else:
            frame += b'\x7f' + length.to_bytes(8, 'big')
        frame += data.encode()
        return frame

    def close(self):
        if self.sock:
            self.sock.close()
            print("WebSocket-Verbindung geschlossen.")
