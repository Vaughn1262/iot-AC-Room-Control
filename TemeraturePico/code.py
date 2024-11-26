import time
import socketpool
import wifi
import busio
import board
import os
from adafruit_ahtx0 import AHTx0

# WiFi setup
print("Connecting to WiFi")
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
print("Connected to WiFi")

# I2C and temperature sensor setup
i2c = busio.I2C(board.GP17, board.GP16)
sensor = AHTx0(i2c)

# Socket pool for communication
pool = socketpool.SocketPool(wifi.radio)
server_ip = "192.168.1.42"  # IP address of the server
server_port = 5001          # Port for temperature data

# Function to send temperature data
def send_temperature():
    try:
        temperature = sensor.temperature
        humidity = sensor.relative_humidity
        message = f"Temperature: {temperature:.2f} C, Humidity: {humidity:.2f} %"
        
        print(f"Sending data to {server_ip}:{server_port} -> {message}")
        
        # Connect to the server
        with pool.socket(socketpool.AF_INET, socketpool.SOCK_STREAM) as sock:
            sock.connect((server_ip, server_port))
            sock.sendall(message.encode("utf-8"))
            
            # Receive acknowledgment
            response = sock.recv(1024).decode("utf-8").strip()
            print("Server response:", response)
    except Exception as e:
        print("Error sending temperature data:", e)

# Main loop
while True:
    send_temperature()
    time.sleep(10)  # Send temperature data every 10 seconds
