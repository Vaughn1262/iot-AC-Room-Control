# This is for the Pi Pico that will get temperature data and send it to the main pico over the network


import time
import board
import microcontroller
import adafruit_ahtx0
import busio

i2c = busio.I2C(board.GP3, board.GP2)
sensor = adafruit_ahtx0.AHTx0(i2c)