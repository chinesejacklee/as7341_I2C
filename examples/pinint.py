#
# Example of pin interrupts of the AS7341
#

from time import sleep_ms
from machine import I2C, SoftI2C, Pin

# i2c = SoftI2C(scl=Pin(27), sda=Pin(33))
i2c = I2C(0)#
print("Detected devices at I2C-addresses:", i2c.scan())

from as7341 import *
sensor = AS7341(i2c, address=87)    # temp

intpin  = Pin(4, Pin.IN)

sensor.measureMode = 0
sensor.enableSpectralInterrupt(1)
sensor.setatime(20)
sensor.setastep(17999)
sensor.setagain(1)

try:
    while True:
        sensor.clearInterrupt()
        print("pinINT is ", "high" if intpin.value() else "low")

        sensor.startMeasure(0)
        sensor.readSpectralDataOne()
        print("Clear {:d}".format(sensor.CLEAR))
        sensor.interrupt()
        print("pinINT is ", "high" if intpin.value() else "low")

        print('-----------------------')

except KeyboardInterrupt:
    print("Interrupted from keyboard")

#
