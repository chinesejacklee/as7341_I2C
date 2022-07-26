#
# Example of reading all channels of the AS7341
#

from time import sleep_ms
from machine import I2C, SoftI2C, Pin

# i2c = SoftI2C(scl=Pin(27), sda=Pin(33))
i2c = I2C(0)#
print("Detected devices at I2C-addresses:", i2c.scan())

from as7341 import *
sensor = AS7341(i2c, address=87)    # temp

sensor.measureMode = SPM            #
sensor.setatime(100)                # 100 ASTEPS
sensor.setastep(999)                # ASTEP 2.78 ms
sensor.setagain(6)                  # factor 32 (about middle between .5 and 512)

try:
    while True:

        sensor.readSpectralDataOne()
        print('F1 (405-425nm): {:d}'.format(sensor.F1))
        print('F2 (435-455nm): {:d}'.format(sensor.F2))
        print('F3 (470-490nm): {:d}'.format(sensor.F3))
        print('F4 (505-525nm): {:d}'.format(sensor.F4))
        print('Clear: {:d}'.format(sensor.CLEAR))
        print('NIR: {:d}'.format(sensor.NIR))

        sensor.readSpectralDataTwo()
        print('F5 (545-565nm): {:d}'.format(sensor.F5))
        print('F6 (580-600nm): {:d}'.format(sensor.F6))
        print('F7 (620-640nm): {:d}'.format(sensor.F7))
        print('F8 (670-690nm): {:d}'.format(sensor.F8))
        print('Clear: {:d}'.format(sensor.CLEAR))
        print('NIR: {:d}'.format(sensor.NIR))

        print('------------------------')

        sleep_ms(2000)

        # Adjust the brightness of the LED lamp
        # sensor.controlLed(19)

except KeyboardInterrupt:
    print("Interrupted from keyboard")

#
