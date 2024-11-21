import time
import socketpool
import wifi
import board
import busio
import os
from adafruit_ahtx0 import AHTx0

# Connect to WiFi
print("Connecting to WiFi...")
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
print(f"Connected to WiFi, IP Address: {wifi.radio.ipv4_address}")

# Set up I2C and temperature sensor
i2c = busio.I2C(board.GP17, board.GP16)
try:
    sensor = AHTx0(i2c)
except Exception as e:
    print(f"Error initializing sensor: {e}")
    sensor = None

# Initialize socket pool
pool = socketpool.SocketPool(wifi.radio)

# Server IP and Port
SERVER_IP = "192.168.1.42"
SERVER_PORT = 5000

def send_temperature():
    """Send temperature and humidity data to the server."""
    if not sensor:
        print("Sensor not initialized. Skipping data send.")
        return

    # Get temperature and humidity readings
    try:
        temperature = sensor.temperature
        humidity = sensor.relative_humidity
        data = f"Temperature: {temperature:.2f}°C, Humidity: {humidity:.2f}%"
        print(f"Sending data: {data}")
    except Exception as e:
        print(f"Error reading sensor data: {e}")
        return

    # Create a socket and send data
    try:
        with pool.socket(pool.AF_INET, pool.SOCK_STREAM) as s:
            s.settimeout(5)  # Set a timeout for the connection
            print(f"Connecting to server at {SERVER_IP}:{SERVER_PORT}...")
            s.connect((SERVER_IP, SERVER_PORT))
            s.send(data.encode("utf-8"))
            print("Data sent successfully.")
    except Exception as e:
        print(f"Error sending data: {e}")
    finally:
        time.sleep(5)  # Prevent rapid retries in case of failure

# Main loop
while True:
    send_temperature()
    time.sleep(10)  # Adjust as needed
