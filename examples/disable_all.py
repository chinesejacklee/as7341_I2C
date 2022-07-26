
#
# Example of disabling LED and sensors
#

from machine import I2C, SoftI2C, Pin

# i2c = SoftI2C(scl=Pin(27), sda=Pin(33))
i2c = I2C(0)
print("Detected devices at I2C-addresses:", i2c.scan())

from as7341 import *
sensor = AS7341(i2c, address=87)    # temp

try:
    sensor.enableLED(0)             # turn off LED
    sensor.disableALL()             # turn off other
    print("All enablers turned off !")

except KeyboardInterrupt:
    print("Interrupted from keyboard")

#
