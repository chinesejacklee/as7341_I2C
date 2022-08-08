#
# Example of reading all channels of the AS7341
#

import sys
from time import sleep_ms
from machine import I2C, SoftI2C, Pin

# i2c = SoftI2C(scl=Pin(27), sda=Pin(33))
i2c = I2C(0)
addrlist = " ".join(["0x{:02X}".format(x) for x in i2c.scan()])
print("Detected devices at I2C-addresses:", addrlist)

from as7341 import *
sensor = AS7341(i2c)
if not sensor.isconnected():
    print("Failed to contact AS7341, terminating")
    sys.exit(1)

sensor.measureMode = AS7341_SPM     # (abbrev. of AS7341_CONFIG_INT_MODE_SPM)
sensor.setatime(100)                # 100 ASTEPS
sensor.setastep(999)                # ASTEP 2.78 ms
sensor.setagain(6)                  # factor 32 (about middle between .5 and 512)

def show_lowmem():
    # print first 20 bytes of AS7341 memory
    lowmem = bytearray(20)
    i2c.readfrom_mem_into(AS7341_I2C_ADDRESS, 0, lowmem)
    print(" ".join(["{:02X}".format(lowmem[i]) for i in range(len(lowmem))]))

try:
    while True:

        sensor.readSpectralDataOne()
        show_lowmem()
        print('F1 (405-425nm): {:d}'.format(sensor.F1))
        print('F2 (435-455nm): {:d}'.format(sensor.F2))
        print('F3 (470-490nm): {:d}'.format(sensor.F3))
        print('F4 (505-525nm): {:d}'.format(sensor.F4))
        print('Clear: {:d}'.format(sensor.CLEAR))
        print('NIR: {:d}'.format(sensor.NIR))

        sensor.readSpectralDataTwo()
        show_lowmem()
        print('F5 (545-565nm): {:d}'.format(sensor.F5))
        print('F6 (580-600nm): {:d}'.format(sensor.F6))
        print('F7 (620-640nm): {:d}'.format(sensor.F7))
        print('F8 (670-690nm): {:d}'.format(sensor.F8))
        print('Clear: {:d}'.format(sensor.CLEAR))
        print('NIR: {:d}'.format(sensor.NIR))

        print('------------------------')

        sleep_ms(5000)

        # Adjust the brightness of the LED lamp
        # sensor.controlLed(19)

except KeyboardInterrupt:
    print("Interrupted from keyboard")

#
