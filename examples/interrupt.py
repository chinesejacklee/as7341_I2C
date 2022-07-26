#
# Example of interrupt handling of the AS7341
#

from machine import I2C, SoftI2C, Pin

# i2c = SoftI2C(scl=Pin(27), sda=Pin(33))
i2c = I2C(0)#
print("Detected devices at I2C-addresses:", i2c.scan())

from as7341 import *
sensor = AS7341(i2c, address=87)    # temp

sensor.measureMode = 0
sensor.enableSpectralInterrupt(1)
sensor.setatime(100)
sensor.setastep(999)
sensor.setagain(6)
sensor.setThresholds(300, 10000)
sensor.setInterruptPersistence(0)
sensor.setSpectralThresholdChannel(4)

try:
    while True:
        sensor.clearInterrupt()
        sensor.startMeasure(0)
        sensor.readSpectralDataOne()
        print("Clear: {:d}".format(sensor.CLEAR))
        sensor.INTerrupt()
        print('-----------------------\r\n')

except KeyboardInterrupt:
    print("Interrupted from keyboard")

#
