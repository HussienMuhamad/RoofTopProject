import network
import socket
import time

def connect_to_wifi(ssid, password):
    """Verbindet den C6 mit dem WLAN."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    print("Verbindung zu WLAN wird hergestellt...")
    while not wlan.isconnected():
        pass

    print("WLAN verbunden:", wlan.ifconfig())

def send_sensor_data(server_ip, port):
    """Sendet Sensordaten an den Server."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, port))

    while True:
        sensor_data = "Temp: 24.5°C, Humidity: 60%"  # Beispiel-Daten
        client_socket.send(sensor_data.encode('utf-8'))
        print(f"Daten gesendet: {sensor_data}")
        time.sleep(5)

    client_socket.close()

def main():
    ssid = "Your_SSID"
    password = "Your_Password"
    server_ip = "Server_IP"  # Ersetze dies mit der IP des Core2
    port = 8080

    connect_to_wifi(ssid, password)
    send_sensor_data(server_ip, port)

if __name__ == "__main__":
    main()
