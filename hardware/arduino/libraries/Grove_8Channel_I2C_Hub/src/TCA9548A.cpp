    
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

#include "TCA9548A.h"

#ifdef SOFTWAREWIRE
  #include <SoftwareWire.h>
#else   
  #include <Wire.h>
#endif

template<class T>
TCA9548A<T>::TCA9548A(void)
{
   
}

template<class T>
TCA9548A<T>::~TCA9548A(void)
{
   
}

template<class T>
void TCA9548A<T>::begin(T &wire, uint8_t address)
{
     this->_address = address;
     this->_wire = &wire;
     this->_channels = 0x00;
     this->_wire->begin();

     this->closeAll();  // defalut close all channel;
}

template<class T>
void TCA9548A<T>::openChannel(uint8_t channel)
{
    this->_channels |= channel;

    write(this->_channels);
}

template<class T>
void TCA9548A<T>::closeChannel(uint8_t channel)
{  
    this->_channels ^= channel;

    write(this->_channels);
}

template<class T>
void TCA9548A<T>::openAll()
{
    this->_channels = 0xFF;
    write(this->_channels);
}

template<class T>
void TCA9548A<T>::closeAll()
{
    this->_channels = 0x00;
    write(this->_channels);
}


template<class T>
void TCA9548A<T>::write(uint8_t value)
{
    this->_wire->beginTransmission(this->_address);
    this->_wire->write(value);
    this->_wire->endTransmission(true);
}

template<class T>
uint8_t TCA9548A<T>::read()
{
    uint8_t status = 0;
    this->_wire->requestFrom((uint16_t)this->_address, (uint8_t)1, (uint8_t)1);

    if(!this->_wire->available())
        return 255;

    status = this->_wire->read();
    
    this->_channels = status;
    return status;
}

#ifdef SOFTWAREWIRE
  template class TCA9548A<SoftwareWire>;
#else
  template class TCA9548A<TwoWire>;
#endif