# SPDX-FileCopyrightText: 2023 Liz Clark for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import os
import time
import ipaddress
import wifi
import socketpool
import busio
import board
import microcontroller
import displayio
import terminalio

# VAUGHNS CHANGES!!!!!!!!!
import pwmio

from adafruit_display_text import label
import adafruit_displayio_ssd1306
import adafruit_imageload
from digitalio import DigitalInOut, Direction
from adafruit_httpserver import Server, Request, Response, POST
from adafruit_onewire.bus import OneWireBus
from adafruit_ds18x20 import DS18X20

#  onboard LED setup
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = False

# Set up PWM on GPIO 15 VAUGHNS CHANGES!!!!!!!!!
Fan_PWM = pwmio.PWMOut(board.GP0, frequency=2500, duty_cycle=0)

# Function to set fan speed (0 to 100%) VAUGHNS CHANGES!!!!!!!!
def set_fan_speed(speed):
    if 0 <= speed <= 100:
        duty_cycle = int((speed / 100) * 65535)
        Fan_PWM.duty_cycle = duty_cycle
        return speed
    else:
        print("Speed must be between 0 and 100")



# WiFi setup
print("Connecting to WiFi")
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
print("Connected to WiFi")

# Socket pool and server setup
pool = socketpool.SocketPool(wifi.radio)
http_port = 5000
temp_data_port = 5001
http_server = Server(pool, "/static", port=http_port, debug=True)

# Storage for received temperature data
latest_temperature_data = "No data received yet."

# Data server for temperature communication on port 5001
data_server = pool.socket(socketpool.AF_INET, socketpool.SOCK_STREAM)
data_server.bind(("0.0.0.0", 5001))
data_server.listen(1)
data_server.settimeout(0.5)  # Non-blocking mode
#  font for HTML
font_family = "monospace"
#  the HTML script
#  setup as an f string
#  this way, can insert string variables from code.py directly
#  of note, use {{ and }} if something from html *actually* needs to be in brackets
#  i.e. CSS style formatting
def webpage():
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta http-equiv="Content-type" content="text/html;charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    html{{font-family: {font_family}; background-color: lightgrey;
    display:inline-block; margin: 0px auto; text-align: center;}}
      h1{{color: deeppink; padding: 2vh; font-size: 35px;}}
      p{{font-size: 1.5rem;}}
      .button{{font-family: {font_family};display: inline-block;
      background-color: black; border: none;
      border-radius: 4px; color: white; padding: 16px 40px;
      text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}}
      p.dotted {{margin: auto; height: 50px;
      width: 75%; font-size: 25px; text-align: center;}}
    </style>
    </head>
    <body>
    <title>Pico W HTTP Server</title>
    <h1>Pico W HTTP Server</h1>
    <p class="dotted">This is a Pico W running an HTTP server with CircuitPython.</p>
    <h1>Control the LED on the Pico W with these buttons:</h1>
    <form accept-charset="utf-8" method="POST">
    <button class="button" name="FAN ON" value="ON" type="submit">LED ON</button></a></p></form>
    <p><form accept-charset="utf-8" method="POST">
    <button class="button" name="FAN OFF" value="OFF" type="submit">LED OFF</button></a></p></form>
    </body></html>
    """
    return html

    #  route default static IP
@server.route("/")
def base(request: Request):  # pylint: disable=unused-argument
    #  serve the HTML f string
    #  with content type text/html
    return Response(request, f"{webpage()}", content_type='text/html')

#  if a button is pressed on the site
@server.route("/", POST)
def buttonpress(request: Request):
    #  get the raw text
    raw_text = request.raw_request.decode("utf8")
    print(raw_text)
    #  if the led on button was pressed
    if "ON" in raw_text:
        #  turn on the onboard LED
        led.value = True

        # Vaughns changes 
        set_fan_speed(100)

    #  if the led off button was pressed
    if "OFF" in raw_text:
        #  turn the onboard LED off
        led.value = False

        # Vaughns changes
        set_fan_speed(0)
    
    #  reload site
    return Response(request, f"{webpage()}", content_type='text/html')

print("starting server..")
# startup the server
try:
    server.start(str(wifi.radio.ipv4_address))
    print("Listening on http://%s:80" % wifi.radio.ipv4_address)
#  if the server fails to begin, restart the pico w
except OSError:
    time.sleep(5)
    print("restarting..")
    microcontroller.reset()
ping_address = ipaddress.ip_address("8.8.4.4")

clock = time.monotonic() #  time.monotonic() holder for server ping

# Socket for temperature data
temp_data_socket = pool.socket()
temp_data_socket.bind((str(wifi.radio.ipv4_address), temp_data_port))
temp_data_socket.listen(1)  # Allow one connection at a time

print(f"Listening for temperature data on port {temp_data_port}")

while True:
    try:
        # Poll HTTP server
        server.poll()
    except Exception as e:
        print("HTTP server error:", e)
    
    try:
        # Check for temperature data
        temp_client, _ = temp_data_socket.accept()
        data = temp_client.recv(1024).decode("utf-8").strip()
        if data:
            print("Received temperature data:", data)
            latest_temperature_data = data

            # Acknowledge receipt
            temp_client.send(b"Temperature data received successfully.")
        temp_client.close()
        # Poll HTTP server for requests
        http_server.poll()
    except OSError:  # No connection available, continue
        pass
    except Exception as e:
        print("Temperature server error:", e)