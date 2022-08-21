#
# Example of pin interrupts of the AS7341
#

import sys
from time import sleep_ms
from machine import I2C, SoftI2C, Pin

# i2c = SoftI2C(scl=Pin(27), sda=Pin(33))
i2c = I2C(0)#
print("Detected devices at I2C-addresses:", i2c.scan())

from as7341 import *

sensor = AS7341(i2c)
if not sensor.isconnected():
    print("Failed to contact AS7341, terminating")
    sys.exit(1)

intpin  = Pin(4, Pin.IN)            # ESP32 pin
sensor.set_spectral_interrupt(1)

sensor.set_atime(29)                # 30 ASTEPS
sensor.set_astep(599)               # 1.67 ms
sensor.set_again(4)                 # factor 8 (with pretty much light)

try:
    while True:
        sensor.clear_interrupt()
        print("pinINT is ", "high" if intpin.value() else "low")
        sensor.start_measure("F1F4CN")
        _,_,_,_,clear,_ = sensor.get_spectral_data()
        print("Clear {:d}".format(clear))
        if sensor.check_interrupt():
            print("Interrupt detected!")
        else:
            print("no interrupts ....")
        print("pinINT is ", "high" if intpin.value() else "low")

        sleep_ms(3000)

except KeyboardInterrupt:
    print("Interrupted from keyboard")

#
