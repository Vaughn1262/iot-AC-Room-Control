# This is for the Pi Pico that will get temperature data and send it to the main pico over the network
#Currently, this program communicates with the temp sensor and prints out the current readings every 2 seconds

import board
import busio
import time
import adafruit_ahtx0
from adafruit_bus_device.i2c_device import I2CDevice
DEVICE_ADDRESS = 0x38

comm_port = busio.I2C(board.GP5, board.GP4)
aht = adafruit_ahtx0.AHTx0(comm_port, DEVICE_ADDRESS)

temperature = aht.temperature
relative_humidity = aht.relative_humidity

while True:
    print("\nTemperature: %0.1f C" % aht.temperature)
    print("Humidity: %0.1f %%" % aht.relative_humidity)
    time.sleep(2)