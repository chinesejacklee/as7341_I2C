
#
# Example of blinking LED with different intensity
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

try:
    while True:
        sensor.enableLED(True)
        print("Blink LED 4 mA, 3 times")
        for _ in range(3):
            sensor.controlLED(4)
            sleep_ms(500)
            sensor.controlLED(0)
            sleep_ms(500)
        print("Blink LED 20 mA, 3 times")
        for _ in range(3):
            sensor.controlLED(20)
            sleep_ms(500)
            sensor.controlLED(0)
            sleep_ms(500)

except KeyboardInterrupt:
    print("Interrupted from keyboard")
    sensor.controlLED(0)        # LED off
    sensor.enableLED(False)
