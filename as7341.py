
"""
This file licensed under the MIT License and incorporates work covered by
the following copyright and permission notice:

The MIT License (MIT)

Copyright (c) 2022-2022 Rob Hamerling

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Rob Hamerling, Version 0.0, July 2022

 Original by WaveShare for Raspberry Pi, part of:
    https://www.waveshare.com/w/upload/b/b3/AS7341_Spectral_Color_Sensor_code.7z

 Adapted to Micropython, such as:
    - requiring specification of I2C interface
    - pythonized (in stead of straight forward conversion from C to Python)
    - many changes of function names
    - some code optimization, esp. I2C communications
    - several other corrections and improvements!

"""

from time import sleep_ms

AS7341_I2C_ADDRESS = const(0X39)

# registers ASTATUS, ITIME and CHx_DATA in address range 0x60--0x6F not accessed

AS7341_CONFIG      = const(0X70)
AS7341_STAT        = const(0X71)
AS7341_EDGE        = const(0X72)
AS7341_GPIO        = const(0X73)
AS7341_LED         = const(0X74)

AS7341_ENABLE      = const(0X80)
AS7341_ATIME       = const(0X81)
AS7341_WTIME       = const(0X83)

AS7341_SP_TH_LOW   = const(0x84)
AS7341_SP_TH_L_LSB = const(0X84)
AS7341_SP_TH_L_MSB = const(0X85)
AS7341_SP_TH_HIGH  = const(0x86)
AS7341_SP_TH_H_LSB = const(0X86)
AS7341_SP_TH_H_MSB = const(0X87)

AS7341_AUXID       = const(0X90)
AS7341_REVID       = const(0X91)
AS7341_ID          = const(0X92)
AS7341_STATUS      = const(0X93)
AS7341_ASTATUS     = const(0X94)
AS7341_CH_DATA     = const(0x95)    # start of the 6 channel counts
AS7341_CH0_DATA_L  = const(0X95)
AS7341_CH0_DATA_H  = const(0X96)
AS7341_CH1_DATA_L  = const(0X97)
AS7341_CH1_DATA_H  = const(0X98)
AS7341_CH2_DATA_L  = const(0X99)
AS7341_CH2_DATA_H  = const(0X9A)
AS7341_CH3_DATA_L  = const(0X9B)
AS7341_CH3_DATA_H  = const(0X9C)
AS7341_CH4_DATA_L  = const(0X9D)
AS7341_CH4_DATA_H  = const(0X9E)
AS7341_CH5_DATA_L  = const(0X9F)
AS7341_CH5_DATA_H  = const(0XA0)

AS7341_STATUS_2    = const(0XA3)
AS7341_STATUS_3    = const(0XA4)
AS7341_STATUS_5    = const(0XA6)
AS7341_STATUS_6    = const(0XA7)
AS7341_CFG_0       = const(0XA9)
AS7341_CFG_1       = const(0XAA)
AS7341_CFG_3       = const(0XAC)
AS7341_CFG_6       = const(0XAF)
AS7341_CFG_8       = const(0XB1)
AS7341_CFG_9       = const(0XB2)
AS7341_CFG_10      = const(0XB3)
AS7341_CFG_12      = const(0XB5)
AS7341_PERS        = const(0XBD)
AS7341_GPIO_2      = const(0XBE)

AS7341_ASTEP       = const(0xCA)
AS7341_ASTEP_L     = const(0XCA)
AS7341_ASTEP_H     = const(0XCB)
AS7341_AGC_GAIN_MAX = const(0XCF)

AS7341_AZ_CONFIG   = const(0XD6)
AS7341_FD_TIME_1   = const(0XD8)
AS7341_FD_TIME_2   = const(0XDA)
AS7341_FD_CFG0     = const(0XD7)
AS7341_FD_STATUS   = const(0XDB)

AS7341_INTENAB     = const(0XF9)
AS7341_CONTROL     = const(0XFA)
AS7341_FIFO_MAP    = const(0XFC)
AS7341_FIFO_LVL    = const(0XFD)
AS7341_FDATA       = const(0xFE)
AS7341_FDATA_L     = const(0XFE)
AS7341_FDATA_H     = const(0XFF)

INPUT              = const(0)
OUTPUT             = const(1)
F1F4CLEARNIR      = const(0)
F5F8CLEARNIR      = const(1)
SPM               = const(0)
SYNS              = const(1)
SYND              = const(3)

adsz = const(16)        # with use of EEPROM as standin for AS7341

class AS7341:
    def __init__(self, i2c, address=AS7341_I2C_ADDRESS):
        # specification of active I2C object expected
        self.bus = i2c
        self.address = address
        self.buffer1 = bytearray(1)     # I2C I/O buffer for byte
        self.buffer2 = bytearray(2)     # I2C I/O buffer for word
        self.buffer13 = bytearray(13)   # I2C I/O buffer for ASTATUS + all channels
        self.F1 = 0                     # count
        self.F2 = 0
        self.F3 = 0
        self.F4 = 0
        self.F5 = 0
        self.F6 = 0
        self.F7 = 0
        self.F8 = 0
        self.NIR = 0
        self.CLEAR = 0
        self.enable(True)
        self.measureMode = SPM          # default mode

    def __read_byte(self, reg):
        try:
            self.bus.readfrom_mem_into(self.address, reg, self.buffer1, addrsize=adsz)
            return self.buffer1[0]                      # return integer value
        except Exception as err:
            print("I2C read_byte at 0x{:02X}, error".format(reg), err)
            return -1                                   # indication 'no receive'

    def __read_word(self, reg):
        try:
            self.bus.readfrom_mem_into(self.address, reg, self.buffer2, addrsize=adsz)
            return int.from_bytes(self.buffer2, 'little')   # return word value
        except Exception as err:
            print("I2C read_word at 0x{:02X}, error".format(reg), err)
            return -1                                   # indication 'no receive'

    def __read_all_channels(self):
        # read all channels, return list of 6 integer values
        try:
            self.bus.readfrom_mem_into(self.address, AS7341_ASTATUS, self.buffer13, addrsize=adsz)
            x = [int.from_bytes(self.buffer13[1 + 2*i : 3 + 2*i], 'little') for i in range(6)]
            return x
        except Exception as err:
            print("I2C read_all_channels at 0x{:02X}, error".format(AS7341_ASTATUS), err)
            return -1                                   # indication 'no receive'

    def __write_byte(self, reg, val):
        self.buffer1[0] = (val & 0xFF)
        try:
            self.bus.writeto_mem(self.address, reg, self.buffer1, addrsize=adsz)
            sleep_ms(10)
        except Exception as err:
            print("I2C write_byte at 0x{:02X}, error".format(reg), err)
            return False
        return True

    def __write_word(self, reg, val):
        self.buffer2[0] = (val & 0xFF)          # low byte
        self.buffer2[1] = (val >> 8) & 0xFF     # high byte
        try:
            self.bus.writeto_mem(self.address, reg, self.buffer2, addrsize=adsz)
            sleep_ms(10)
        except Exception as err:
            print("I2C write_word at 0x{:02X}, error".format(reg), err)
            return False
        return True

    def __write_burst(self, reg, val):
        # write an array of bytes starting at register 'reg'
        try:
            self.bus.writeto_mem(self.address, reg, val, addrsize=adsz)
            sleep_ms(20)
        except Exception as err:
            print("I2C write_burst at 0x{:02X}, error".format(reg), err)
            return False
        return True

    def __setbank(self, bank):
        # select registerbank (1 for regs 0x60-0x74; 0 for 0x80..0xFF)
        data = self.__read_byte(AS7341_CFG_0)
        if bank == 1:
            data |= (1<<4)
        elif bank == 0:
            data &= (~(1<<4))
        self.__write_byte(AS7341_CFG_0, data)

    def enable(self, flag):
        # enable sensor
        data = self.__read_byte(AS7341_ENABLE)
        if flag == True:
            data |= (1<<0)
        else:
            data &= (~(1<<0))
        self.__write_byte(AS7341_ENABLE, data)
        self.__write_byte(0x00, 0x30)

    def enableSpectralMeasure(self, flag):
        # select
        data = self.__read_byte(AS7341_ENABLE)
        if flag == True:
            data |= (1<<1)
        else:
            data &= (~(1<<1))
        self.__write_byte(AS7341_ENABLE, data)

    def enableSMUX(self, flag):
        # select
        data=self.__read_byte(AS7341_ENABLE)
        if flag == True:
            data |= (1<<4)
        else:
            data &= (~(1<<4))
        self.__write_byte(AS7341_ENABLE, data)

    def enableFlickerDetection(self, flag):
        # select
        data=self.__read_byte(AS7341_ENABLE)
        if flag == True:
            data |= (1<<6)
        else:
            data &= (~(1<<6))
        self.__write_byte(AS7341_ENABLE, data)

    def config(self, mode):
        # configure the sensor for a specific mode
        if mode in (SPM, SYNS, SYND):
            self.__setbank(1)
            data = self.__read_byte(AS7341_CONFIG) & (~3)
            data |= mode
            self.__write_byte(AS7341_CONFIG, data)
            self.__setbank(0)

    def F1F4_Clear_NIR(self):
        data = b'\x30\x01\x00\x00\x00\x42\x00\x00\x50\x00\x00\x00\x20\x04\x00\x30\x01\x50\x00\x06'
        self.__write_burst(0x00, data)

    def F5F8_Clear_NIR(self):
        data = b'\x00\x00\x00\x40\x02\x00\x10\x03\x50\x10\x03\x00\x00\x00\x24\x00\x00\x50\x00\x06'
        self.__write_burst(0x00, data)

    def FDConfig(self):
        data = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x60'
        self.__write_burst(0x00, data)

    def startMeasure(self, mode):
        data = self.__read_byte(AS7341_CFG_0)
        data &= (~(1<<4))
        self.__write_byte(AS7341_CFG_0, data)
        self.enableSpectralMeasure(False)
        self.__write_byte(0xAF, 0x10)

        if mode == F1F4CLEARNIR:
            self.F1F4_Clear_NIR()
        elif mode == F5F8CLEARNIR:
            self.F5F8_Clear_NIR()
            self.enableSMUX(True)
        if self.measureMode == SYNS:
            self.setGpioMode(INPUT)
            self.config(SYNS)
        elif self.measureMode == SPM:
            self.config(SPM)
        self.enableSpectralMeasure(True)
        if self.measureMode == SPM:
            while (self.measureComplete() == False):
                sleep_ms(100)

    def readFlickerData(self):
        flicker=0
        data = self.__read_byte(AS7341_CFG_0)
        data = data & (~(1<<4))
        self.__write_byte(AS7341_CFG_0, data)
        self.enableSpectralMeasure(False)
        self.write_byte(0xAF, 0x10)
        self.FDConfig()
        self.enableSMUX(True)
        self.enableSpectralMeasure(True)
        retry = 100
        if retry == 0:
            print(' data access error')
        self.__enableFlickerDetection(True)
        sleep_ms(600)
        flicker = self.__read_byte(AS7341_STATUS)
        self.__enableFlickerDetection(False)
        if flicker == 37:
            flicker = 100
        elif flicker == 40:
            flicker = 0
        elif flicker == 42:
            flicker = 120
        elif flicker == 44:
            flicker = 1
        elif flicker == 45:
            flicker = 2
        else:
            flicker = 2
        return flicker

    def measureComplete(self):
        status = self.__read_byte(AS7341_STATUS_2)
        if status & (1<<6):
            return True
        else:
            return False

    def getchannelData(self, channel):
        # read count of a single channel (channel in range 0..5)
        channelData = self.__read_word(AS7341_CH_DATA + channel * 2)
        sleep_ms(50)
        return channelData

    def readSpectralDataOne(self):
        # obtain counts of channels F1..F4 + CLEAR + NIR
        self.startMeasure(6)        # RobH: value 0 or 1 expected?
        self.F1, self.F2, self.F3, self.F4, self.CLEAR, self.NIR = self.__read_all_channels()

    def readSpectralDataTwo(self):
        # obtain counts of channels F5..F8 + CLEAR + NIR
        self.startMeasure(1)
        self.F5, self.F6, self.F7, self.F8, self.CLEAR, self.NIR = self.__read_all_channels()

    def setGpioMode(self, mode):
        data = self.__read_byte(AS7341_GPIO_2)
        if mode == INPUT:
            data = data | (1<<2)
        if mode == OUTPUT:
            data = data & (~(1<<2))
        self.__write_byte(AS7341_GPIO_2, data)

    def setatime(self, value):
        # set number of intergration steps (range 0..255 -> 1..256 ASTEPs)
        self.__write_byte(AS7341_ATIME, value & 0xFF)

    def setastep(self, value):
        # set ASTEP size (range 0..65534 -> 2.78 usec .. 182 msec)
        if 0 <= value <= 65534:
            self.__write_word(AS7341_ASTEP_L, value)

    def setagain(self, value):
        # set AGAIN (range 0..10 -> gain factor 0.5 .. 512)
        if 0 <= value <= 10:
            self.__write_byte(AS7341_CFG_1, value)

    def enableLED(self, flag):
        # enable (PWM) control of LED
        self.__setbank(1)
        data = self.__read_byte(AS7341_CONFIG)
        data1 = self.__read_byte(AS7341_LED)
        if flag == True:
            data |= (1<<3)
            data1 |= (1<<7)
        else:
            data &= (~(1<<3))
            data1 &= (~(1<<7))
        self.__write_byte(AS7341_LED, data1)
        self.__write_byte(AS7341_CONFIG, data)
        self.__setbank(0);


    def controlLED(self, current):
        # Control current of LED in milliamperes
        # The allowed current is limited to the range 4..20 mA
        # Specification outside this range results in LED OFF
        self.__setbank(1)
        if 4 <= current <= 20:                  # within limits
            data = self.__read_byte(AS7341_CONFIG)
            data |= (1<<3)                      # activate LED control register
            self.__write_byte(AS7341_CONFIG, data)
            data = 0x80 + ((current - 4) // 2)  # LED on
        else:
            data == 0                           # LED off
        self.__write_byte(AS7341_LED, data)
        sleep_ms(100)
        self.__setbank(0)

    def interrupt(self):
        data = self.__read_byte(AS7341_STATUS)
        if data & 0x80:
            print('Spectral interrupt generation！')

    def clearInterrupt(self):
        self.__write_byte(AS7341_STATUS, 0xFF)

    def enableSpectralInterrupt(self, flag):
        data = self.__read_byte(AS7341_INTENAB)
        if flag == True:
            self.__write_byte(AS7341_INTENAB, data | (1<<3))
        else:
            self.__write_byte(AS7341_INTENAB, data & (~(1<<3)))

    def setInterruptPersistence(self, value):
        self.__write_byte(AS7341_PERS, value)
        # self.__read_byte(AS7341_PERS)

    def setThresholds(self, lo, hi):
        # Set thresholds (when lo < hi)
        if lo < hi:
            self.__write_word(AS7341_SP_TH_L_LSB, lo)
            self.__write_word(AS7341_SP_TH_H_LSB, hi)
            sleep_ms(20)

    def setSpectralThresholdChannel(self, value):
        self.__write_byte(AS7341_CFG_12, value)

    def getThresholds(self):
        # obtain low and high thresholds
        lo = self.__read_word(AS7341_SP_TH_LOW)
        hi = self.__read_word(AS7341_SP_TH_HIGH)
        return [lo, hi]

    def synsINT_sel(self):
        self.__write_byte(AS7341_CONFIG, 0x05)

    def disableALL(self):
        self.__write_byte(AS7341_ENABLE, 0x02)

#
