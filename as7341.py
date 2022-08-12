
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
    - pythonized (in stead of 'literal' translation of C code)
    - instance of AS7341 requires specification of I2C interface
    - added I2C read/write error detection
    - added check for connected AS7341 incl. device ID
    - some code optimization (esp. adding I2C word/block reads/writes)
    - moved SMUX settings for predefined channel mappings to a dictionary
      and as a separate file to allow changes or additional configurations
      by the user without changing the driver
    - changes of names of functions and constants (incl. came case -> underscore sep.)
    - added comments, doc-strings with explanation and/or argumentation
    - several other corrections and improvements

  Remarks:
    - Automatic Gain Control (AGC) is not supported
    - No provisions for SYND mode

"""

from time import sleep_ms

from as7341_smux_select import *            # predefined SMUX configurations


AS7341_I2C_ADDRESS  = const(0X39)           # I2C address of AS7341
AS7341_ID_VALUE     = const(0x24)           # AS7341 Part Number Identification
                                            # (excl 2 low order bits)

# Symbolic names for registers and some selected bit fields
# Note: ASTATUS, ITIME and CHx_DATA in address range 0x60--0x6F are not used
AS7341_CONFIG       = const(0X70)
AS7341_CONFIG_INT_MODE_SPM  = const(0x00)
AS7341_MODE_SPM             = AS7341_CONFIG_INT_MODE_SPM    # alias
AS7341_CONFIG_INT_MODE_SYNS = const(0x01)
AS7341_MODE_SYNS            = AS7341_CONFIG_INT_MODE_SYNS   # alias
AS7341_CONFIG_INT_MODE_SYND = const(0x03)
AS7341_MODE_SYND            = AS7341_CONFIG_INT_MODE_SYND   # alias
AS7341_CONFIG_INT_SEL       = const(0x04)
AS7341_CONFIG_LED_SEL       = const(0x08)
AS7341_STAT         = const(0X71)
AS7341_STAT_READY     = const(0x01)
AS7341_STAT_WAIT_SYNC = const(0x02)
AS7341_EDGE         = const(0X72)
AS7341_GPIO         = const(0X73)
AS7341_GPIO_PD_INT    = const(0x01)
AS7341_GPIO_PD_GPIO   = const(0x02)
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
AS7341_ASTATUS_ASAT_STATUS  = const(0x80)
AS7341_ASTATUS_AGAIN_STATUS = const(0x0F)
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
AS7341_FD_STATUS_FD_100HZ      = const(0X01)
AS7341_FD_STATUS_FD_120HZ      = const(0X02)
AS7341_FD_STATUS_FD_100_VALID  = const(0X04)
AS7341_FD_STATUS_FD_120_VALID  = const(0X08)
AS7341_FD_STATUS_FD_SAT_DETECT = const(0X10)
AS7341_FD_STATUS_FD_MEAS_VALID = const(0X20)
AS7341_INTENAB      = const(0XF9)
AS7341_INTENAB_SP_IEN = const(0x08)
AS7341_CONTROL      = const(0XFA)
AS7341_FIFO_MAP     = const(0XFC)
AS7341_FIFO_LVL     = const(0XFD)
AS7341_FDATA        = const(0xFE)
AS7341_FDATA_L      = const(0XFE)
AS7341_FDATA_H      = const(0XFF)


class AS7341:
    """ Class for AS7341: 11 Channel Multi-Spectral Digital Sensor """

    def __init__(self, i2c, addr=AS7341_I2C_ADDRESS):
        """ specification of active I2C object is mandatory
            specification of I2C address of AS7341 is optional """
        self.__bus = i2c
        self.__address = addr
        self.__buffer1 = bytearray(1)                   # I2C I/O buffer for byte
        self.__buffer2 = bytearray(2)                   # I2C I/O buffer for word
        self.__buffer13 = bytearray(13)                 # I2C I/O buffer for ASTATUS + 6 channels
        self.__measuremode = AS7341_MODE_SPM   # default mode
        self.__connected = self.__verify_connection()   # check AS7341 presence
        if self.__connected:
            self.enable(True)                           # power-on

    """ --------- 'private' functions ----------- """

    def __read_byte(self, reg):
        """ read byte, return byte (integer) value """
        try:
            self.__bus.readfrom_mem_into(self.__address, reg, self.__buffer1)
            return self.__buffer1[0]                      # return integer value
        except Exception as err:
            print("I2C read_byte at 0x{:02X}, error".format(reg), err)
            return -1                                   # indication 'no receive'


    def __read_word(self, reg):
        """ read 2 consecutive bytes, return integer value (little Endian) """
        try:
            self.__bus.readfrom_mem_into(self.__address, reg, self.__buffer2)
            return int.from_bytes(self.__buffer2, 'little')   # return word value
        except Exception as err:
            print("I2C read_word at 0x{:02X}, error".format(reg), err)
            return -1                                   # indication 'no receive'


    def __read_all_channels(self):
        """ read ASTATUS register and all channels, return list of 6 integer values """
        try:
            self.__bus.readfrom_mem_into(self.__address, AS7341_ASTATUS, self.__buffer13)
            return [int.from_bytes(self.__buffer13[1 + 2*i : 3 + 2*i], 'little') for i in range(6)]
        except Exception as err:
            print("I2C read_all_channels at 0x{:02X}, error".format(AS7341_ASTATUS), err)
            return []                                   # empty list


    def __write_byte(self, reg, val):
        """ write a single byte to the specified register """
        self.__buffer1[0] = (val & 0xFF)
        try:
            self.__bus.writeto_mem(self.__address, reg, self.__buffer1)
            sleep_ms(10)
        except Exception as err:
            print("I2C write_byte at 0x{:02X}, error".format(reg), err)
            return False
        return True


    def __write_word(self, reg, val):
        """ write a word as 2 bytes (little endian encoding) to adresses 'reg' +0 and +1 """
        self.__buffer2[0] = (val & 0xFF)          # low byte
        self.__buffer2[1] = (val >> 8) & 0xFF     # high byte
        try:
            self.__bus.writeto_mem(self.__address, reg, self.__buffer2)
            sleep_ms(20)
        except Exception as err:
            print("I2C write_word at 0x{:02X}, error".format(reg), err)
            return False
        return True


    def __write_burst(self, reg, val):
        """ write an array of bytes to consucutive addresses starting <reg> """
        try:
            self.__bus.writeto_mem(self.__address, reg, val)
            sleep_ms(100)
        except Exception as err:
            print("I2C write_burst at 0x{:02X}, error".format(reg), err)
            return False
        return True


    def __verify_connection(self):
        """ Check if AS7341 is connected """
        id = self.__read_byte(AS7341_ID)        # obtain Part Number ID
        if id < 0:                              # read error
            print("Failed to contact AS7341 at I2C address 0x{:02X}".format(self.__address))
            return False
        else:
            if not (id & (~3)) == AS7341_ID_VALUE:  # ID in bits 7..2 bits
                print("No AS7341: ID = 0x{:02X}, expected 0x{:02X}".format(id, AS7341_ID_VALUE))
                return False
            else:
                return True


    def __setbank(self, bank):
        """ select registerbank (1 for regs 0x60-0x74; 0 for 0x80..0xFF) """
        if bank in (0,1):
            data = self.__read_byte(AS7341_CFG_0)
            if bank == 1:
                data |= AS7341_CFG_0_REG_BANK
            else:
                data &= (~AS7341_CFG_0_REG_BANK)
            self.__write_byte(AS7341_CFG_0, data)

    def __measure_complete(self):
        """ check if measurement completed (return True) or otherwise return False """
        status = self.__read_byte(AS7341_STATUS_2)
        return True if (status & AS7341_STATUS_2_AVALID) else False


    """ ----------- 'public' functions ----------- """

    def isconnected(self):
        """ determine if AS7341 is successfully initialized (True/False) """
        return self.__connected


    def enable(self, flag=True):
        """ enable device (power on, disable spectral Measurement: SP_EN=0) """
        data = self.__read_byte(AS7341_ENABLE)
        if flag == True:
            data |= AS7341_ENABLE_PON
        else:
            data &= (~AS7341_ENABLE_PON)
        self.__write_byte(AS7341_ENABLE, data)


    def enable_spectral_measurement(self, flag):
        """ enable (flag == True) spectral measurement or otherwise disable it """
        data = self.__read_byte(AS7341_ENABLE)
        if flag == True:
            data |= AS7341_ENABLE_SP_EN
        else:
            data &= (~AS7341_ENABLE_SP_EN)
        self.__write_byte(AS7341_ENABLE, data)


    def enable_smux(self, flag):
        """ enable (flag == True) SMUX or otherwise disable it """
        data=self.__read_byte(AS7341_ENABLE)
        if flag == True:
            data |= AS7341_ENABLE_SMUXEN
        else:
            data &= (~AS7341_ENABLE_SMUXEN)
        self.__write_byte(AS7341_ENABLE, data)


    def enable_flicker_detection(self, flag):
        """ enable (flag == True) flicker detection or otherwise disable it """
        data = self.__read_byte(AS7341_ENABLE)
        if flag == True:
            data |= AS7341_ENABLE_FDEN
        else:
            data &= (~AS7341_ENABLE_FDEN)
        self.__write_byte(AS7341_ENABLE, data)


    def set_measure_mode(self, mode):
        """ configure the AS7341 for a specific interrupt mode """
        if mode in (AS7341_CONFIG_INT_MODE_SPM,     # meas. started by SP_EN
                    AS7341_CONFIG_INT_MODE_SYNS,    # meas. started by GPIO
                    AS7341_CONFIG_INT_MODE_SYND):   # meas. started by GPIO + EDGE
            self.__setbank(1)                       # CONFIG register is in bank 1
            self.__measuremode = self.__read_byte(AS7341_CONFIG) & (~3)  # discard current mode
            self.__measuremode |= mode                # set new mode
            self.__write_byte(AS7341_CONFIG, self.__measuremode)
            self.__setbank(0)


    def channel_select(self, selection):
        """ select one from a series of predefined SMUX configurations
            <selection> should be a key in dictionary AS7341_SMUX_SELECT """
        if selection in AS7341_SMUX_SELECT:
            self.__write_burst(0x00, AS7341_SMUX_SELECT[selection])
        else:
            print(selection, "is unknown in AS7341_SMUX_SELECT")


    def start_measure(self, selection):
        """ select SMUX configuration, prepare and start measurement """
        data = self.__read_byte(AS7341_CFG_0)
        data &= (~AS7341_CFG_0_LOW_POWER)           # escape from low-power mode
        self.__write_byte(AS7341_CFG_0, data)
        self.enable_spectral_measurement(False)       # quiesce
        self.__write_byte(AS7341_CFG_6, AS7341_CFG_6_SMUX_CMD_WRITE) # mode
        if self.__measuremode == AS7341_CONFIG_INT_MODE_SPM:
            self.channel_select(selection)
            self.enable_smux(True)
        elif self.__measuremode == AS7341_CONFIG_INT_MODE_SYNS:
            self.channel_select(selection)
            self.enable_smux(True)
            self.set_gpio_mode(AS7341_GPIO_2_GPIO_IN)
        self.enable_spectral_measurement(True)
        if self.__measuremode == AS7341_CONFIG_INT_MODE_SPM:
            while not self.__measure_complete():
                sleep_ms(50)


    def read_flicker_data(self):
        """ determine flicker frequency, returns 100, 120 or 0 """
        data = self.__read_byte(AS7341_CFG_0)
        data = data & (~AS7341_CFG_0_LOW_POWER)     # escape from low power mode
        self.__write_byte(AS7341_CFG_0, data)
        self.enable_spectral_measurement(False)
        self.__write_byte(AS7341_CFG_6, AS7341_CFG_6_SMUX_CMD_WRITE)
        # print("FD_STATUS", "0x{:02X}".format(self.__read_byte(AS7341_FD_STATUS)))
        self.channel_select("FD")                   # select flicker detection only
        self.enable_smux(True)
        self.enable_spectral_measurement(True)
        self.enable_flicker_detection(True)         # ATIME and AGAIN
        sleep_ms(600)
        fd_status = self.__read_byte(AS7341_FD_STATUS)
        print("FD_STATUS", "0x{:02X}".format(fd_status))
        self.enable_flicker_detection(False)
        self.__write_byte(AS7341_FD_STATUS, 0x3F)   # clear all FD STATUS bits
        if fd_status & AS7341_FD_STATUS_FD_MEAS_VALID:  # FD meas. complete
            if ((fd_status & AS7341_FD_STATUS_FD_100_VALID) and
                (fd_status & AS7341_FD_STATUS_FD_100HZ)):
                return 100
            elif ((fd_status & AS7341_FD_STATUS_FD_120_VALID) and
                  (fd_status & AS7341_FD_STATUS_FD_120HZ)):
                return 120
        return 0



    def get_channel_data(self, channel):
        """ read count of a single channel (channel in range 0..5) """
        data = 0                            # default
        if 0 <= channel <= 5:
            data = self.__read_word(AS7341_CH_DATA + channel * 2)
            sleep_ms(50)
        return data


    def read_spectral_data(self, selection):
        """ configure SMUX for <selection> of the channels
            obtain counts of all channels
            return a tuple of 6 counts (integers) of the channels """
        self.start_measure(selection)
        return self.__read_all_channels()   # return a tuple!


    def set_gpio_mode(self, mode):
        """ Configure GPIO pin (one of 3 Pin modes or inverted) """
        if mode in (AS7341_GPIO_2_GPIO_IN, AS7341_GPIO_2_GPIO_OUT,
                    AS7341_GPIO_2_GPIO_IN_EN, AS7341_GPIO_2_GPIO_INV):
            self.__write_byte(AS7341_GPIO_2, mode)


    def set_atime(self, value):
        """ set number of integration steps (range 0..255 -> 1..256 ASTEPs) """
        self.__write_byte(AS7341_ATIME, value & 0xFF)


    def set_astep(self, value):
        """ set ASTEP size (range 0..65534 -> 2.78 usec .. 182 msec) """
        if 0 <= value <= 65534:
            self.__write_word(AS7341_ASTEP, value)


    def set_again(self, value):
        """ set AGAIN (range 0..10 -> gain factor 0.5 .. 512)
            value     0    1    2    3    4    5      6     7      8      9     10
            gain:  *0.5 | *1 | *2 | *4 | *8 | *16 | *32 | *64 | *128 | *256 | *512 """
        if 0 <= value <= 10:
            self.__write_byte(AS7341_CFG_1, value)


    def control_led(self, current):
        """ Control current of onboard LED in milliamperes
            LED-current is (here) limited to the range 4..20 mA
            use only even numbers (4,6,8,... etc)
            Specification outside this range results in LED OFF """
        self.__setbank(1)
        if 4 <= current <= 20:                  # within limits: 4..20 mA
            data = self.__read_byte(AS7341_CONFIG)
            data |= AS7341_CONFIG_LED_SEL       # activate LED selection
            self.__write_byte(AS7341_CONFIG, data)
            # print("Reg. CONFIG (0x70) now 0x{:02X}".format(self.__read_byte(0x70)))
            data = AS7341_LED_LED_ACT + ((current - 4) // 2)  # LED on with PWM
        else:
            data = 0                           # LED off (but kept selected), PWM 0
        self.__write_byte(AS7341_LED, data)
        print("reg 0x74 (LED) now 0x{:02X}".format(self.__read_byte(0x74)))
        self.__setbank(0)
        sleep_ms(100)


    def interrupt(self):
        """ Check for Spectral or Flicker Detect saturation interrupt """
        data = self.__read_byte(AS7341_STATUS)
        if data & AS7341_STATUS_ASAT:
            print('Spectral interrupt generation！')
            return True
        else:
            return False


    def clear_interrupt(self):
        """ clear all interrupt signals """
        self.__write_byte(AS7341_STATUS, 0xFF)


    def enable_spectral_interrupt(self, flag):
        """ enable (flag == True) or otherwise disable spectral interrupts """
        data = self.__read_byte(AS7341_INTENAB)
        if flag == True:
            data |= AS7341_INTENAB_SP_IEN
        else:
            data &= (~AS7341_INTENAB_SP_IEN)
        self.__write_byte(AS7341_INTENAB, data)


    def set_interrupt_persistence(self, value):
        """ configure interrupt persistance """
        if 0 <= value <= 15:
            self.__write_byte(AS7341_PERS, value)


    def set_spectral_threshold_channel(self, value):
        """ select channel (0..4) for interrupts, persistence and AGC """
        if 0 <= value <= 4:
            self.__write_byte(AS7341_CFG_12, value)


    def set_thresholds(self, lo, hi):
        """ Set thresholds (when lo < hi) """
        if lo < hi:
            self.__write_word(AS7341_SP_TH_LOW, lo)
            self.__write_word(AS7341_SP_TH_HIGH, hi)
            sleep_ms(20)


    def get_thresholds(self):
        """ obtain and return tuple with low and high threshold values """
        lo = self.__read_word(AS7341_SP_TH_LOW)
        hi = self.__read_word(AS7341_SP_TH_HIGH)
        return (lo, hi)


    def syns_int_sel(self):
        """ select SYNS mode and signal SYNS interrupt on Pin INT """
        self.__write_byte(AS7341_CONFIG, AS7341_CONFIG_INT_SEL | AS7341_CONFIG_INT_MODE_SYNS)


    def disable_all(self):
        """ disable all functions (but keep power on) """
        self.__write_byte(AS7341_ENABLE, AS7341_ENABLE_PON)

#
