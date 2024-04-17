/*
 * The MIT License (MIT)
 * 
 * Author: Hongtai Liu (lht856@foxmail.com)
 * 
 * Copyright (C) 2019  Seeed Technology Co.,Ltd. 
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */


#ifndef SEEED_TCA9548A_H
#define SEEED_TCA9548A_H

//#define SOFTWAREWIRE

#if ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif

#ifdef SOFTWAREWIRE
  #include <SoftwareWire.h>
#else   
  #include <Wire.h>
#endif

/**************************************************************************
    I2C ADDRESS/BITS
**************************************************************************/
#define TCA9548_DEFAULT_ADDRESS 0x70

/**************************************************************************
          Channel STATUS
  -------------------------------------------------------
 ┆  B7  ┆  B6  ┆  B5  ┆  B4  ┆  B3  ┆  B2  ┆  B1  ┆  B0  ┆                                                                |
 ┆-------------------------------------------------------┆
 ┆  ch7 ┆  ch6 ┆ ch5  ┆  ch4 ┆  ch3 ┆  ch2 ┆  ch1 ┆  ch0 ┆ 
 ˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉˉ  
**************************************************************************/
#define TCA_CHANNEL_0 0x1
#define TCA_CHANNEL_1 0x2
#define TCA_CHANNEL_2 0x4
#define TCA_CHANNEL_3 0x8
#define TCA_CHANNEL_4 0x10
#define TCA_CHANNEL_5 0x20
#define TCA_CHANNEL_6 0x40
#define TCA_CHANNEL_7 0x80

template <class T>
class TCA9548A
{
    public:
        TCA9548A();
        ~TCA9548A();

        void begin(T &wire = Wire, uint8_t address = TCA9548_DEFAULT_ADDRESS);

        void openChannel(uint8_t channel);
        void closeChannel(uint8_t channel);
        inline uint8_t readStatus(){return read();};
 
        void closeAll();
        void openAll();

    private:

        T * _wire;
        uint8_t _address; 
        uint8_t _channels; // status of channel

        void write(uint8_t val);
        uint8_t read();

    
};

#endif /*SEEED_TCA9548A_H*/