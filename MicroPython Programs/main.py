# Author: Michael Cieslak
# Date: April 4th, 2024
# Note: This Script connectes to a BME280 sensor and OLED display through an I2C bus
# and this was written to be used with a Rasberry Pi PICO W.
#
# import libraries used in script
import machine
import bme280
import utime
import time
import math
from ssd1306 import SSD1306_I2C
from machine import Pin

# Define I2C Pins
I2C_SDA_PIN = 4
I2C_SCL_PIN = 5

# Setup the BME280 sensor on the I2C bus
i2c=machine.I2C(0,sda=machine.Pin(I2C_SDA_PIN), scl=machine.Pin(I2C_SCL_PIN), freq=400000)
bme = bme280.BME280(i2c=i2c)

# Setup the OLED display connection on I2C bus
oled = SSD1306_I2C(128, 64, i2c)

# Setup Interupt Pin for Sel Input
pin = Pin(6, Pin.IN, Pin.PULL_UP)
interrupt_flag=0
debounce_time=0
def callback(pin):
    global interrupt_flag, debounce_time
    if (time.ticks_ms()-debounce_time) > 300:
        interrupt_flag= 1
        debounce_time=time.ticks_ms()
pin.irq(trigger=Pin.IRQ_FALLING, handler=callback)

# Intitalize arrays for used for running average
temp_arr = [0] * 3
hum_arr = [0] * 3
pres_arr = [0] * 3

# variables used for sequencing and settings in program
i=0
sel = 1


#Start the Display as blank
oled.fill(0)
oled.show()

# Always run this after setup
while True:
    # Check if the button was pressed
    if interrupt_flag is 1:
        interrupt_flag=0
        if sel == 1:
            sel = 0
        else:
            sel = 1
            
    # Take measurements and calculate values
    readings = bme.read_compensated_data()
    temp_arr[i] = readings[0] / 100.0
    pres_arr[i] = (readings[1] / 256.0) / 100.0
    hum_arr[i] = readings[2] / 1024.0
    
    # take average of recorded measurements
    temp = 0
    humidity = 0
    pressure = 0
    for x in range(0,3):
        temp = temp + temp_arr[x]
        humidity = humidity + hum_arr[x]
        pressure = pressure + pres_arr[x]
    temp = temp / 3
    humidity = humidity / 3
    pressure = pressure / 3
    altitude = ((math.log((pressure * 100.0) / 101325) * 287.053) * (temp + 459.67)*(5/9))/-9.8
        
    
    # Format Strings for output
    line1 = "Temp: " + str("{:.1f}".format(temp)) + "C"
    if sel == 1:
        temp = (9/5) * temp + 32
        line1 = "Temp: " + str("{:.1f}".format(temp)) + "F"
    line2 = "Hum:  " + str("{:.1f}".format(humidity)) + "%"
    line3 = "Pres: " + str("{:.1f}".format(pressure)) + "hPa"
    line4 = "Alt:  " + str("{:.1f}".format(altitude)) + "m"
    
    # Output Values to Display
    oled.fill(0)
    oled.text(line1,0,0)
    oled.text(line2,0,10)
    oled.text(line3,0,20)
    oled.text(line4,0,30)
    oled.show()
    
    # interate through i which is used for moving average
    if i>1:
        i = 0
    else:
        i = i + 1
        
    # Pause program for half a second
    utime.sleep_ms(200)

