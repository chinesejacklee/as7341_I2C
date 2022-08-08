
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

 Converted to Micropython for use with MicroPython devices such as ESP32
    - pythonized (in stead of straight forward conversion from C to Python)
    - requiring specification of I2C interface
    - added I2C read/write error detection
    - added check for connected AS7341 incl. device ID
    - some code optimization (esp. I2C word/block reads/writes)
    - changes of names of functions and constants
    - added comments with explanation and/or argumentation
    - several other corrections and improvements!

"""

from time import sleep_ms

AS7341_I2C_ADDRESS  = const(0X39)           # I2C address of AS7341
AS7341_ID_VALUE     = const(0x24)           # Part Number Identification (excl 2 low order bits)

# registers ASTATUS, ITIME and CHx_DATA in address range 0x60--0x6F not used

AS7341_CONFIG       = const(0X70)
AS7341_CONFIG_INT_MODE_SPM  = const(0x00)
AS7341_SPM                  = AS7341_CONFIG_INT_MODE_SPM    # alias
AS7341_CONFIG_INT_MODE_SYNS = const(0x01)
AS7341_SYNS                 = AS7341_CONFIG_INT_MODE_SYNS   # alias
AS7341_CONFIG_INT_MODE_SYND = const(0x03)
AS7341_SYND                 = AS7341_CONFIG_INT_MODE_SYND   # alias
AS7341_CONFIG_INT_SEL       = const(0x04)
AS7341_CONFIG_LED_SEL       = const(0x08)
AS7341_STAT         = const(0X71)
AS7341_EDGE         = const(0X72)
AS7341_GPIO         = const(0X73)
AS7341_LED          = const(0X74)
AS7341_LED_LED_ACT    = const(0x80)

AS7341_ENABLE       = const(0X80)
AS7341_ENABLE_PON     = const(0x01)
AS7341_ENABLE_SP_EN   = const(0x02)
AS7341_ENABLE_WEN     = const(0x08)
AS7341_ENABLE_SMUXEN  = const(0x10)
AS7341_ENABLE_FDEN    = const(0x40)
AS7341_ATIME        = const(0X81)
AS7341_WTIME        = const(0X83)

AS7341_SP_TH_LOW    = const(0x84)
AS7341_SP_TH_L_LSB  = const(0X84)
AS7341_SP_TH_L_MSB  = const(0X85)
AS7341_SP_TH_HIGH   = const(0x86)
AS7341_SP_TH_H_LSB  = const(0X86)
AS7341_SP_TH_H_MSB  = const(0X87)

AS7341_AUXID        = const(0X90)
AS7341_REVID        = const(0X91)
AS7341_ID           = const(0X92)
AS7341_STATUS       = const(0X93)
AS7341_STATUS_ASAT    = const(0x80)
AS7341_STATUS_AINT    = const(0x08)
AS7341_STATUS_FINT    = const(0x04)
AS7341_STATUS_C_INT   = const(0x02)
AS7341_STATUS_SINT    = const(0x01)
AS7341_ASTATUS      = const(0X94)       # start of bulk read (incl 6 counts)
AS7341_CH_DATA      = const(0x95)       # start of the 6 channel counts
AS7341_CH0_DATA_L   = const(0X95)
AS7341_CH0_DATA_H   = const(0X96)
AS7341_CH1_DATA_L   = const(0X97)
AS7341_CH1_DATA_H   = const(0X98)
AS7341_CH2_DATA_L   = const(0X99)
AS7341_CH2_DATA_H   = const(0X9A)
AS7341_CH3_DATA_L   = const(0X9B)
AS7341_CH3_DATA_H   = const(0X9C)
AS7341_CH4_DATA_L   = const(0X9D)
AS7341_CH4_DATA_H   = const(0X9E)
AS7341_CH5_DATA_L   = const(0X9F)
AS7341_CH5_DATA_H   = const(0XA0)

AS7341_STATUS_2     = const(0XA3)
AS7341_STATUS_2_AVALID = const(0x40)
AS7341_STATUS_3     = const(0XA4)
AS7341_STATUS_5     = const(0XA6)
AS7341_STATUS_6     = const(0XA7)
AS7341_CFG_0        = const(0XA9)
AS7341_CFG_0_WLONG     = const(0x04)
AS7341_CFG_0_REG_BANK  = const(0x10)        # datasheet fig 82 (! fig 32)
AS7341_CFG_0_LOW_POWER = const(0x20)
AS7341_CFG_1        = const(0XAA)
AS7341_CFG_3        = const(0XAC)
AS7341_CFG_6        = const(0XAF)
AS7341_CFG_6_SMUX_CMD_ROM   = const(0x00)
AS7341_CFG_6_SMUX_CMD_READ  = const(0x08)
AS7341_CFG_6_SMUX_CMD_WRITE = const(0x10)
AS7341_CFG_8        = const(0XB1)
AS7341_CFG_9        = const(0XB2)
AS7341_CFG_10       = const(0XB3)
AS7341_CFG_12       = const(0XB5)
AS7341_PERS         = const(0XBD)
AS7341_GPIO_2       = const(0XBE)
AS7341_GPIO_2_GPIO_IN    = const(0x01)
AS7341_GPIO_2_GPIO_OUT   = const(0x02)
AS7341_GPIO_2_GPIO_IN_EN = const(0x04)
AS7341_GPIO_2_GPIO_INV   = const(0x08)
AS7341_ASTEP        = const(0xCA)
AS7341_ASTEP_L      = const(0XCA)
AS7341_ASTEP_H      = const(0XCB)
AS7341_AGC_GAIN_MAX = const(0XCF)

AS7341_AZ_CONFIG    = const(0XD6)
AS7341_FD_TIME_1    = const(0XD8)
AS7341_FD_TIME_2    = const(0XDA)
AS7341_FD_CFG0      = const(0XD7)
AS7341_FD_STATUS    = const(0XDB)

AS7341_INTENAB      = const(0XF9)
AS7341_INTENAB_SP_IEN = const(0x08)
AS7341_CONTROL      = const(0XFA)
AS7341_FIFO_MAP     = const(0XFC)
AS7341_FIFO_LVL     = const(0XFD)
AS7341_FDATA        = const(0xFE)
AS7341_FDATA_L      = const(0XFE)
AS7341_FDATA_H      = const(0XFF)

# additional constants

AS7341_F1F4CLEARNIR = const(0)
AS7341_F5F8CLEARNIR = const(1)



class AS7341:
    def __init__(self, i2c, addr=AS7341_I2C_ADDRESS):
        # specification of active I2C object expected
        self.bus = i2c
        self.address = addr
        self.buffer1 = bytearray(1)     # I2C I/O buffer for byte
        self.buffer2 = bytearray(2)     # I2C I/O buffer for word
        self.buffer13 = bytearray(13)   # I2C I/O buffer for ASTATUS + all 6 channels
        self.F1 = 0                     # counts
        self.F2 = 0
        self.F3 = 0
        self.F4 = 0
        self.F5 = 0
        self.F6 = 0
        self.F7 = 0
        self.F8 = 0
        self.NIR = 0
        self.CLEAR = 0
        self.measureMode = AS7341_CONFIG_INT_MODE_SPM   # default interrupt mode
        self.__connected = self.__verify_connection()   # check AS7341 presence
        if self.__connected:
            self.enable(True)                           # power-on,


    def __read_byte(self, reg):
        # read byte, return byte (integer) value
        try:
            self.bus.readfrom_mem_into(self.address, reg, self.buffer1)
            return self.buffer1[0]                      # return integer value
        except Exception as err:
            print("I2C read_byte at 0x{:02X}, error".format(reg), err)
            return -1                                   # indication 'no receive'


    def __read_word(self, reg):
        # read 2 consecutive bytes, return integer value (little Endian)
        try:
            self.bus.readfrom_mem_into(self.address, reg, self.buffer2)
            return int.from_bytes(self.buffer2, 'little')   # return word value
        except Exception as err:
            print("I2C read_word at 0x{:02X}, error".format(reg), err)
            return -1                                   # indication 'no receive'


    def __read_all_channels(self):
        # read status register and all channels, return list of 6 integer values
        try:
            self.bus.readfrom_mem_into(self.address, AS7341_ASTATUS, self.buffer13)
            return [int.from_bytes(self.buffer13[1 + 2*i : 3 + 2*i], 'little') for i in range(6)]
        except Exception as err:
            print("I2C read_all_channels at 0x{:02X}, error".format(AS7341_ASTATUS), err)
            return []                                   # empty list


    def __write_byte(self, reg, val):
        # write a single byte to the specified register
        self.buffer1[0] = (val & 0xFF)
        try:
            self.bus.writeto_mem(self.address, reg, self.buffer1)
            sleep_ms(10)
        except Exception as err:
            print("I2C write_byte at 0x{:02X}, error".format(reg), err)
            return False
        return True


    def __write_word(self, reg, val):
        # write a word as 2 bytes (little endian encoding) to adresses 'reg' +0 and +1
        self.buffer2[0] = (val & 0xFF)          # low byte
        self.buffer2[1] = (val >> 8) & 0xFF     # high byte
        try:
            self.bus.writeto_mem(self.address, reg, self.buffer2)
            sleep_ms(10)
        except Exception as err:
            print("I2C write_word at 0x{:02X}, error".format(reg), err)
            return False
        return True


    def __write_burst(self, reg, val):
        # write an array of bytes to consucutive addresses starting 'reg'
        try:
            self.bus.writeto_mem(self.address, reg, val)
            sleep_ms(20)
        except Exception as err:
            print("I2C write_burst at 0x{:02X}, error".format(reg), err)
            return False
        return True


    def __verify_connection(self):
        id = self.__read_byte(AS7341_ID)        # obtain Part Number ID
        if id < 0:                              # read error
            print("Failed to contact AS7341 at I2C address 0x{:02X}".format(self.address))
            return False
        else:
            if not (id & (~3)) == AS7341_ID_VALUE:  # ID in bits 7..2 bits
                print("No AS7341: ID = 0x{:02X}, expected 0x{:02X}".format(id, AS7341_ID_VALUE))
                return False
            else:
                return True


    def __setbank(self, bank):
        # select registerbank (1 for regs 0x60-0x74; 0 for 0x80..0xFF)
        if bank in (0,1):
            data = self.__read_byte(AS7341_CFG_0)
            if bank == 1:
                data |= AS7341_CFG_0_REG_BANK
            else:
                data &= (~AS7341_CFG_0_REG_BANK)
            self.__write_byte(AS7341_CFG_0, data)


    def isconnected(self):
        # determine if AS7341 is successfully initialized (True/False)
        return self.__connected


    def enable(self, flag=True):
        # enable device (power on, disable spectral Measurement: SP_EN = 0)
        data = self.__read_byte(AS7341_ENABLE)
        if flag == True:
            data |= AS7341_ENABLE_PON
        else:
            data &= (~AS7341_ENABLE_PON)
        self.__write_byte(AS7341_ENABLE, data)
        self.__write_byte(0x00, 0x30)               # RobH ??


    def enableSpectralMeasurement(self, flag):
        # enable (flag == True) spectral measurement or otherwise disable it
        data = self.__read_byte(AS7341_ENABLE)
        if flag == True:
            data |= AS7341_ENABLE_SP_EN
        else:
            data &= (~AS7341_ENABLE_SP_EN)
        self.__write_byte(AS7341_ENABLE, data)


    def enableSMUX(self, flag):
        # enable (flag == True) SMUX or otherwise disable it
        data=self.__read_byte(AS7341_ENABLE)
        if flag == True:
            data |= AS7341_ENABLE_SMUXEN
        else:
            data &= (~AS7341_ENABLE_SMUXEN)
        self.__write_byte(AS7341_ENABLE, data)


    def enableFlickerDetection(self, flag):
        # enable (flag = True) flicker detection or otherwise disable it
        data=self.__read_byte(AS7341_ENABLE)
        if flag == True:
            data |= AS7341_ENABLE_FDEN
        else:
            data &= (~AS7341_ENABLE_FDEN)
        self.__write_byte(AS7341_ENABLE, data)


    def config(self, mode):
        # configure the AS7341 for a specific interrupt mode
        if mode in (AS7341_CONFIG_INT_MODE_SPM,
                    AS7341_CONFIG_INT_MODE_SYNS,
                    AS7341_CONFIG_INT_MODE_SYND):
            self.__setbank(1)                       # CONFIG register is in bank 1
            data = self.__read_byte(AS7341_CONFIG) & (~3)   # discard current mode
            data |= mode                            # set new mode
            self.__write_byte(AS7341_CONFIG, data)
            self.__setbank(0)


    def F1F4_Clear_NIR(self):
        # configure SMUX for reading F1..F4 + Clear + NIR
        data = b'\x30\x01\x00\x00\x00\x42\x00\x00\x50\x00\x00\x00\x20\x04\x00\x30\x01\x50\x00\x06'
        self.__write_burst(0x00, data)


    def F5F8_Clear_NIR(self):
        # configure SMUX for reading F5..F8 + Clear + NIR
        data = b'\x00\x00\x00\x40\x02\x00\x10\x03\x50\x10\x03\x00\x00\x00\x24\x00\x00\x50\x00\x06'
        self.__write_burst(0x00, data)


    def FDConfig(self):
        # configure SMUX exclusively for Flicker detection
        data = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.__write_burst(0x00, data)


    def startMeasure(self, selection):
        # select SMUX configuration
        # prepare and start measurement
        data = self.__read_byte(AS7341_CFG_0)
        data &= (~AS7341_CFG_0_LOW_POWER)           # abandon low-power mode
        self.__write_byte(AS7341_CFG_0, data)
        self.enableSpectralMeasurement(False)
        self.__write_byte(AS7341_CFG_6, AS7341_CFG_6_SMUX_CMD_WRITE)
        if selection == AS7341_F1F4CLEARNIR:
            self.F1F4_Clear_NIR()
            self.enableSMUX(True)
        elif selection == AS7341_F5F8CLEARNIR:
            self.F5F8_Clear_NIR()
            self.enableSMUX(True)
        if self.measureMode == AS7341_CONFIG_INT_MODE_SYNS:
            self.setGpioMode(AS7341_INPUT)
            self.config(AS7341_CONFIG_INT_MODE_SYNS)
        elif self.measureMode == AS7341_CONFIG_INT_MODE_SPM:
            self.config(AS7341_CONFIG_INT_MODE_SPM)
        self.enableSpectralMeasurement(True)
        if self.measureMode == AS7341_CONFIG_INT_MODE_SPM:
            while (self.measureComplete() == False):
                sleep_ms(100)


    def readFlickerData(self):
        # determine flicker
        flicker=0
        data = self.__read_byte(AS7341_CFG_0)
        data = data & (~AS7341_CFG_0_LOW_POWER)     # not in low power mode
        self.__write_byte(AS7341_CFG_0, data)
        self.enableSpectralMeasurement(False)
        self.write_byte(AS7341_CFG_6, AS7341_CFG_6_SMUX_CMD_READ)
        self.FDConfig()
        self.enableSMUX(True)
        self.enableSpectralMeasurement(True)
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
        # check if measurement completed (return True) or otherwise return False
        status = self.__read_byte(AS7341_STATUS_2)
        return True if (status & AS7341_STATUS_2_AVALID) else False


    def getchannelData(self, channel):
        # read count of a single channel (channel in range 0..5)
        channelData = self.__read_word(AS7341_CH_DATA + channel * 2)
        sleep_ms(50)
        return channelData


    def readSpectralDataOne(self):
        # obtain counts of channels F1..F4 + CLEAR + NIR
        # self.startMeasure(6)          # RobH: strange value
        self.startMeasure(AS7341_F1F4CLEARNIR)
        self.F1, self.F2, self.F3, self.F4, self.CLEAR, self.NIR = self.__read_all_channels()


    def readSpectralDataTwo(self):
        # obtain counts of channels F5..F8 + CLEAR + NIR
        self.startMeasure(AS7341_F5F8CLEARNIR)
        self.F5, self.F6, self.F7, self.F8, self.CLEAR, self.NIR = self.__read_all_channels()


    def setGpioMode(self, mode):
        # Configure GPIO pin in one of 4 allowed modes
        if mode in (AS7341_GPIO_2_GPIO_IN, AS7341_GPIO_2_GPIO_OUT,
                    AS7341_GPIO_2_GPIO_IN_EN, AS7341_GPIO_2_GPIO_INV):
            self.__write_byte(AS7341_GPIO_2, mode)


    def setatime(self, value):
        # set number of intergration steps (range 0..255 -> 1..256 ASTEPs)
        self.__write_byte(AS7341_ATIME, value & 0xFF)


    def setastep(self, value):
        # set ASTEP size (range 0..65534 -> 2.78 usec .. 182 msec)
        if 0 <= value <= 65534:
            self.__write_word(AS7341_ASTEP, value)


    def setagain(self, value):
        # set AGAIN (range 0..10 -> gain factor 0.5 .. 512)
        # value     0    1    2    3    4    5      6     7      8      9     10
        # gain:  *0.5 | *1 | *2 | *4 | *8 | *16 | *32 | *64 | *128 | *256 | *512
        if 0 <= value <= 10:
            self.__write_byte(AS7341_CFG_1, value)


    def enableLED(self, flag):
        # enable (flag == True) LED (any earlier PWM setting preserved)
        self.__setbank(1)                       # CONFIG and LED registers both in bank 1
        data1 = self.__read_byte(AS7341_CONFIG)
        data2 = self.__read_byte(AS7341_LED)
        if flag == True:
            data1 |= AS7341_CONFIG_LED_SEL      # enable LED selection
            data2 |= AS7341_LED_LED_ACT         # activate LED
        else:
            data1 &= (~AS7341_CONFIG_LED_SEL)
            data2 &= (~AS7341_LED_LED_ACT)
        self.__write_byte(AS7341_LED, data2)
        self.__write_byte(AS7341_CONFIG, data1)
        self.__setbank(0);


    def controlLED(self, current):
        # Control current of LED in milliamperes
        # The allowed LED-current is limited to the range 4..20 mA
        # use only even numbers (4,6,8,... etc)
        # Specification outside this range results in LED OFF
        self.__setbank(1)
        if 4 <= current <= 20:                  # within limits: 4..20 mA
            data = self.__read_byte(AS7341_CONFIG)
            data |= AS7341_CONFIG_LED_SEL       # activate LED selection
            self.__write_byte(AS7341_CONFIG, data)
            print("reg 0x70 (CONFIG) now 0x{:02X}".format(self.__read_byte(0x70)))
            data = AS7341_LED_LED_ACT + ((current - 4) // 2)  # LED on with PWM
        else:
            data = 0                           # LED off (but keep selected), PWM 0
        self.__write_byte(AS7341_LED, data)
        print("reg 0x74 (LED) now 0x{:02X}".format(self.__read_byte(0x74)))
        self.__setbank(0)
        sleep_ms(100)


    def interrupt(self):
        # Check for Spectra of Flicker Detect saturation interrupt
        data = self.__read_byte(AS7341_STATUS)
        if data & AS7341_STATUS_ASAT:
            print('Spectral interrupt generation！')
            return True
        else:
            return False


    def clearInterrupt(self):
        # clear all interrupt signals
        self.__write_byte(AS7341_STATUS, 0xFF)


    def enableSpectralInterrupt(self, flag):
        # enable (flag == True) or otherwise disable spectral interrupts
        data = self.__read_byte(AS7341_INTENAB)
        if flag == True:
            data |= AS7341_INTENAB_SP_IEN
        else:
            data &= (~AS7341_INTENAB_SP_IEN)
        self.__write_byte(AS7341_INTENAB, data)


    def setInterruptPersistence(self, value):
        # configure interrupt persistance
        if 0 <= value <= 15:
            self.__write_byte(AS7341_PERS, value)
            # self.__read_byte(AS7341_PERS)


    def setSpectralThresholdChannel(self, value):
        # select channel (0..4) for interrupts, persistence and AGC
        if 0 <= value <= 4:
            self.__write_byte(AS7341_CFG_12, value)


    def setThresholds(self, lo, hi):
        # Set thresholds (when lo < hi)
        if lo < hi:
            self.__write_word(AS7341_SP_TH_LOW, lo)
            self.__write_word(AS7341_SP_TH_HIGH, hi)
            sleep_ms(20)


    def getThresholds(self):
        # obtain and return tuple with low and high threshold values
        lo = self.__read_word(AS7341_SP_TH_LOW)
        hi = self.__read_word(AS7341_SP_TH_HIGH)
        return (lo, hi)


    def synsINT_sel(self):
        # select SYNS mode and signal SYNS interrupt on Pin INT
        self.__write_byte(AS7341_CONFIG, AS7341_CONFIG_INT_SEL | AS7341_CONFIG_INT_MODE_SYNS)


    def disableALL(self):
        # disable all functions but keep power on
        self.__write_byte(AS7341_ENABLE, AS7341_ENABLE_PON)

#
