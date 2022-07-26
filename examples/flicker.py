#
# Example of flicker detection
#

from machine import I2C, SoftI2C, Pin

# i2c = SoftI2C(scl=Pin(27), sda=Pin(33))
i2c = I2C(0)
print("Detected devices at I2C-addresses:", i2c.scan())

from as7341 import *
sensor = AS7341(i2c, address=87)    # temp

try:
    while True:

        flicker_freq = sensor.ReadFlickerData()
        if flicker_freq in (0, 2):
            print("No flicker!")
        elif flicker_freq == 1:
            print("Unknown frequency")
        else:
            print("Flicker frequency: {:d} Hz".format(flicker_freq))

except KeyboardInterrupt:
    print("Interrupted from keyboard")

#
