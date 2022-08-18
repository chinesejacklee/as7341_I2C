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

sensor.set_measure_mode(AS7341_MODE_SPM)
sensor.set_atime(29)                # => 30 ASTEPS
sensor.set_astep(599)               # => 0.6 ms per step
sensor.set_again(4)                 # factor 8 (with pretty much light)

print("Integration time:", sensor.get_integration_time(), "msec")

try:
    while True:
        sensor.start_measure("F1F4CN")      # implicit wait for completion
        f1,f2,f3,f4,clr,nir = sensor.get_spectral_data()   # results
        # show_lowmem()
        print('F1 (405-425nm): {:d}'.format(f1))
        print('F2 (435-455nm): {:d}'.format(f2))
        print('F3 (470-490nm): {:d}'.format(f3))
        print('F4 (505-525nm): {:d}'.format(f4))
        print('Clear: {:d}'.format(clr))
        print('NIR: {:d}'.format(nir))

        sensor.start_measure("F5F8CN")
        f5,f6,f7,f8,clr,nir = sensor.get_spectral_data()
        # show_lowmem()
        print('F5 (545-565nm): {:d}'.format(f5))
        print('F6 (580-600nm): {:d}'.format(f6))
        print('F7 (620-640nm): {:d}'.format(f7))
        print('F8 (670-690nm): {:d}'.format(f8))
        print('Clear: {:d}'.format(clr))
        print('NIR: {:d}'.format(nir))

        sensor.start_measure("F2F7")
        f2,f3,f4,f5,f6,f7 = sensor.get_spectral_data()
        # show_lowmem()
        print('F2 (435-455nm): {:d}'.format(f2))
        print('F3 (470-490nm): {:d}'.format(f3))
        print('F4 (505-525nm): {:d}'.format(f4))
        print('F5 (545-565nm): {:d}'.format(f5))
        print('F6 (580-600nm): {:d}'.format(f6))
        print('F7 (620-640nm): {:d}'.format(f7))

        print('------------------------')
        sleep_ms(5000)


except KeyboardInterrupt:
    print("Interrupted from keyboard")

sensor.disable()

#
