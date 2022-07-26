#
# Example of sysns reading of
#

from time import sleep_ms
from machine import I2C, SoftI2C, Pin

# i2c = SoftI2C(scl=Pin(27), sda=Pin(33))
i2c = I2C(0)#
print("Detected devices at I2C-addresses:", i2c.scan())

as7341 import
sensor = as7341.AS7341(i2c, address=87)    # temp

sensor.measureMode = as7341.SYNS
sensor.ATIME_config(100)
sensor.ASTEP_config(999)
sensor.AGAIN_config(6)

try:
    while True:

        print("Waiting for the GPIO signal...")
        sensor.startMeasure(0)
        while sensor.measureComplete() == 0:
            sleep_ms(100)
        sensor.readSpectralDataOne()
        print("channel1(405-425nm): {:d}".format(sensor.F1))
        print("channel2(435-455nm): {:d}".format(sensor.F2))
        print("channel3(470-490nm): {:d}".format(sensor.F3))
        print("channel4(505-525nm): {:d}".format(sensor.F4))
        print("Clear: {:d}".format(sensor.CLEAR))
        print("NIR: {:d}".format(sensor.NIR))
        print("-----------------------")

except KeyboardInterrupt:
    print("Interrupted from keyboard")

#
