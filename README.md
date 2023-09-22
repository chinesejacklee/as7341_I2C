# micropython-as7341

Micropython driver with:
    Class for AS7341: 11 Channel Multi-Spectral Digital Sensor

Rob Hamerling, Version 0.3, June 2023

Original by WaveShare for Raspberry Pi, part of:
  https://www.waveshare.com/w/upload/b/b3/AS7341_Spectral_Color_Sensor_code.7z

Adapted to Micropython, such as:
  - Specification of active I2C interface is now required.
  - Pythonized (in stead of straight forward conversion from C to Python).
  - Many function names have been changed,
    some functions removed, new functions added.
  - Code optimized, esp. I2C communications.
  - Code corrected, readability improved.
  - Doc-strings and comments added.


## Getting started

  - Select a Micropython device with hardware I2C module, e.g. ESP32.
  - Connect the AS7341 board via an I2C interface (hardware or software).
    Depending on the choice of the I2C interface
    the examples may require a minor modification.
  - Copy as7341.py and as7341_smux_select.py
    (or cross-compiled .mpy versions)
    to the Micropython device.
  - Do the same with the examples.
  - Run one or more of the examples.
    For the examples 'syns', 'pinint' and 'gpio_in_en' the GPIO pin
    should be connected to +3.3V via a 10K resistor and via
    a normally open push-button to GND.


This repository is **work in progress**.
Not sure that all examples are working!
More/better documentation should follow, for now read the comments in the sources!


## Examples

  - as7341_all.py: read several ranges channels
  - as7341_mid_log.py: read middle range channels, log the counts
  - flicker.py: read flicker
  - gpio_in_en.py: show use of GPIO pin for input
  - interrupt.py: use of interrupt pin
  - led_blink_pwm: show control of onboard LED
  - pinint.py: use pin to trigger read-out
  - syns.py: syns-mode, measurement starts with GPIO transition


## Documentation

  - AS7341_AN000666_1-01.pdf - Appplication Note: SMUX Configuration
  - AS7341_DS000504_3-00.pdf - Datasheet: 11-Channel Multi-Spectral Digital Sensor


## Summary of changes

  - 0.1 Improved several 'get' members: return actual device settings
  - 0.2 Removed superfluous instance variables (atime,astep,again)
  - 0.3 Renamed hidden class variables and members:
        single underscore prefix in stead of double underscore.


.
