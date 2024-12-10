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
server_port = 5000            # Webserver listens on port 80

# Function to send temperature data as HTTP POST
def send_temperature():
    try:
        temperature = sensor.temperature
        meas_temperature = temperature  # Sending current temperature as the "goal_temperature"

        # Format the HTTP POST request
        payload = f"meas_temperature={meas_temperature:.2f}"
        request = "POST / HTTP/1.1\r\n" + \
          "Host: " + server_ip + "\r\n" + \
          "Content-Type: application/x-www-form-urlencoded\r\n" + \
          "Content-Length: " + str(len(payload)) + "\r\n" + \
          "\r\n" + \
          payload


        print(f"Sending data to {server_ip}:{server_port} -> {payload}")
        
        # Connect to the webserver
        sock = pool.socket()
        sock.connect((server_ip, server_port))
        sock.send(request.encode("utf-8"))

        ## Receive acknowledgment
        #response = sock.recv(1024).decode("utf-8").strip()
        #print("Server response:", response)
        sock.close()
    except Exception as e:
        print("Error sending temperature data:", e)

# Main loop
while True:
    send_temperature()
    time.sleep(10)  # Send temperature data every 10 seconds