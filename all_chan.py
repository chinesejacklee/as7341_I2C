#
# Elementary test of AS7341 library
#

from time import sleep_ms


from machine import I2C, SoftI2C, Pin

# i2c = SoftI2C(scl=Pin(27), sda=Pin(33))
i2c = I2C(0)
print("Detected devices at I2C-address:", i2c.scan())

from as7341 import *

colori = AS7341(i2c, address=87)    # temp
colori.measureMode = eSpm       #
colori.atime_config(100)        # 100 ASTEPS
colori.astep_config(999)        # ASTEP 2.78 ms
colori.again_config(6)          # factor 32 (about middle between .5 and 512)

try:
    while True:

        colori.startMeasure(6)      # RobH: value 0 or 1 expected?
        colori.readSpectralDataOne()
        print('F1 (405-425nm): {:d}'.format(colori.F1))
        print('F2 (435-455nm): {:d}'.format(colori.F2))
        print('F3 (470-490nm): {:d}'.format(colori.F3))
        print('F4 (505-525nm): {:d}'.format(colori.F4))
        print('Clear: {:d}'.format(colori.CLEAR))
        print('NIR: {:d}'.format(colori.NIR))

        colori.startMeasure(1)
        colori.readSpectralDataTwo()
        print('F5 (545-565nm): {:d}'.format(colori.F5))
        print('F6 (580-600nm): {:d}'.format(colori.F6))
        print('F7 (620-640nm): {:d}'.format(colori.F7))
        print('F8 (670-690nm): {:d}'.format(colori.F8))
        print('Clear: {:d}'.format(colori.CLEAR))
        print('NIR: {:d}'.format(colori.NIR))

        print('------------------------')

        sleep_ms(2000)

        # Adjust the brightness of the LED lamp
        # colori.controlLed(19)

except KeyboardInterrupt:
    print("Interrupted from keyboard")

#
