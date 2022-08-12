# micropython-as7341

Micropython driver with:
    Class for AS7341: 11 Channel Multi-Spectral Digital Sensor

Rob Hamerling, Version 0.0, August 2022

Original by WaveShare for Raspberry Pi, part of:
  https://www.waveshare.com/w/upload/b/b3/AS7341_Spectral_Color_Sensor_code.7z

Adapted to Micropython, such as:
  - requiring specification of I2C interface
  - pythonized (in stead of straight forward conversion from C to Python)
  - many changes of function names
  - some code optimization, esp. I2C communications
  - several other corrections and improvements


## Getting started

This library is under construction.
Not all examples are working.
Documentation should follow, for now read comments in source!


## Examples

  - all_channels.py: read whole range of channels
  - disable_all.py: disable whole sensor
  - flicker.py: read flicker
  - interrupt.py: use of interrupt
  - pinint.py: use pin to trigger read-out
  - syns.py: syns-mode

.
