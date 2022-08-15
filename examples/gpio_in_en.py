#
# Example of use of GPIO pin as input
#

from time import sleep_ms
from machine import I2C, SoftI2C, Pin

# i2c = SoftI2C(scl=Pin(27), sda=Pin(33))
i2c = I2C(0)#
print("Detected devices at I2C-addresses:", i2c.scan())

from as7341 import *
sensor = AS7341(i2c)

sensor.set_gpio_mode(AS7341_GPIO_2_GPIO_IN_EN)  # enable input mode

try:
    while True:
        print("GPIO is ", "high" if sensor.get_gpio_value() else "low")
        sleep_ms(3000)

except KeyboardInterrupt:
    print("Interrupted from keyboard")

sensor.disable()

#
