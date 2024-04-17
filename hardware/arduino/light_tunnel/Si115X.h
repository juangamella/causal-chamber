/* ; -*- mode: C++;-*-

   BSD 3-Clause License

   Copyright (c) 2021, Juan L Gamella
   All rights reserved.

   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

   3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULR PURPOSE ARE
   DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
   FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
   DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
   SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
   CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

/* Note: this code was adapted from the Grove Sunlight Sensor demo: https://github.com/Seeed-Studio/Grove_Sunlight_Sensor */

#ifndef SI115X_H
#define SI115X_H

#include <Arduino.h>
#include <Wire.h>

struct LightReading {
  float ir;
  float vis;
  int ok;
};

class Si115X
{
public:
  typedef enum {
                DEVICE_ADDRESS = 0x53			
  } UnitAddress;

  typedef enum {
                RESET_CMD_CTR = 0x00,
                RESET_SW = 0x01,
                FORCE = 0x11,
                PAUSE = 0x12,
                START = 0x13
  } CommandCodes;

  typedef enum{
               RUNNING = 0b10000000,
               SUSPEND = 0b01000000,
               SLEEP = 0b00100000,
               CMD_ERR = 0b00010000,
               CMD_CTR = 0b00001111,
  } Response0Bits;

  typedef enum {
                INVALID_COMMAND = 0x0,
                INVALID_LOCATION = 0x1,
                ADC_SATURATION = 0x2,
                BUFFER_OVERFLOW = 0x3,
  } ErrorCodes;
  
  typedef enum {	
                PART_ID = 0x00,
                REV_ID = 0x01,
                MFR_ID = 0x02,
                INFO_0 = 0x03,
                INFO_1 = 0x04,
                HOSTIN_3 = 0x07,
                HOSTIN_2 = 0x08,
	
                HOSTIN_0 = 0x0A,
                COMMAND = 0x0B,
                IRQ_ENABLE = 0x0F,
                RESPONSE_0 = 0x11,
                RESPONSE_1 = 0x10,
			
                IRQ_STATUS = 0x12,
                HOSTOUT_0 = 0x13,
                HOSTOUT_1 = 0x14,
                HOSTOUT_2 = 0x15,
                HOSTOUT_3 = 0x16,
                HOSTOUT_4 = 0x17,
                HOSTOUT_5 = 0x18,
                HOSTOUT_6 = 0x19,
                HOSTOUT_7 = 0x1A,
                HOSTOUT_8 = 0x1B,
                HOSTOUT_9 = 0x1C,
                HOSTOUT_10 = 0x1D,
                HOSTOUT_11 = 0x1E,
                HOSTOUT_12 = 0x1F,
                HOSTOUT_13 = 0x20,
                HOSTOUT_14 = 0x21,
                HOSTOUT_15 = 0x22,
                HOSTOUT_16 = 0x23,
                HOSTOUT_17 = 0x24,
                HOSTOUT_18 = 0x25,
                HOSTOUT_19 = 0x26,
                HOSTOUT_20 = 0x27,
                HOSTOUT_21 = 0x28,
                HOSTOUT_22 = 0x29,
                HOSTOUT_23 = 0x2A,
                HOSTOUT_24 = 0x2B,
                HOSTOUT_25 = 0x2C	
  } RegisterAddress;

  typedef enum {		
                I2C_ADDR = 0x00,
                CHAN_LIST = 0x01,

                ADCCONFIG_0 = 0x02,
                ADCSENS_0 = 0x03,
                ADCPOST_0 = 0x04,
                MEASCONFIG_0 = 0x05,
			
                ADCCONFIG_1 = 0x06,
                ADCPOST_1 = 0x08,
                ADCSENS_1 = 0x07,
                MEASCONFIG_1 = 0x09,

                ADCCONFIG_2 = 0x0A,
                ADCSENS_2 = 0x0B,
                ADCPOST_2 = 0x0C,
                MEASCONFIG_2 = 0x0D,

                ADCCONFIG_3 = 0x0E,
                ADCSENS_3 = 0x0F,
                ADCPOST_3 = 0x10,
                MEASCONFIG_3 = 0x11,

                ADCCONFIG_4 = 0x12,
                ADCSENS_4 = 0x13,
                ADCPOST_4 = 0x14,
                MEASCONFIG_4 = 0x15,

                ADCCONFIG_5 = 0x16,
                ADCSENS_5 = 0x17,
                ADCPOST_5 = 0x18,
                MEASCONFIG_5 = 0x19,
			
                MEASRATE_H = 0x1A,
                MEASRATE_L = 0x1B,
                MEASCOUNT_0 = 0x1C,
                MEASCOUNT_1 = 0x1D,
                MEASCOUNT_2 = 0x1E,
			
                LED1_A = 0x1F,
                LED1_B = 0x20,
                LED2_A = 0x21,
                LED2_B = 0x22,
                LED3_A = 0x23,
                LED3_B = 0x24,

                THRESHOLD0_H = 0x25,
                THRESHOLD0_L = 0x26,
                THRESHOLD1_H = 0x27,
                THRESHOLD1_L = 0x28,
                THRESHOLD2_H = 0x29,
                THRESHOLD2_L = 0x2A,

                BURST = 0x2B			
  } ParameterAddress;
		
  // Si115X();
  void write_data(uint8_t addr, uint8_t *data, size_t len);
  int read_register(uint8_t addr, uint8_t reg, int bytesOfData);
  void param_set(uint8_t loc, uint8_t val);
  int param_query(uint8_t loc);
  int send_command(uint8_t code, bool force);
  // bool Begin(void); unused
  uint8_t ReadByte(uint8_t Reg);
  LightReading read_output(void);
};

#endif

// TODO:
//   - Refactor: remove unused functions
//   - Read IR -> read output of channel zero
//   - Implement proper error control with functions that send commands
