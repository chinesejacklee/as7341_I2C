# micropython-as7341

Micropython driver with:
    Class for AS7341: 11 Channel Multi-Spectral Digital Sensor

Rob Hamerling, Version 0.0, August 2022

Original by WaveShare for Raspberry Pi, part of:
  https://www.waveshare.com/w/upload/b/b3/AS7341_Spectral_Color_Sensor_code.7z

Adapted to Micropython, such as:
  - requiring specification of I2C interface
  - pythonized (in stead of straight forward conversion from C to Python)
  - many changes of function names, some functions removed, new functions added
  - code optimization, esp. I2C communications
  - several code corrections and improvements
  - added doc-strings and comments


## Getting started

  - Select a Micropython device with hardware I2C module
  - Connect the AS7341 board via I2C,
    depending on the choice of the I2C interface
    the examples may require a slight modification.
  - Copy as7341.py and as7341_smux_select.py (or cross-compiled .mpy versions)
    to the Micropython device (e.g. ESP32)
  - Do the same with the examples
  - Run one or more of the examples
    For the examples 'syns', 'pinint' and 'gpio_in_en' the GPIO pin should be
    connected to +3.3V via a 10K resistor and via a normally open push-button to GND.


This repository is under construction.
Not sure that all examples are working!
More/better documentation should follow, for now read the comments in source!


## Examples

  - all_channels.py: read whole range of channels
  - flicker.py: read flicker
  - gpio_in_en.py: show use of GPIO pin for input
  - interrupt.py: use of interrupt pin
  - led_blink_pwm: show control of onboard LED
  - pinint.py: use pin to trigger read-out
  - syns.py: syns-mode, measurement starts with GPIO transition

.
