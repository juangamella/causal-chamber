/*
 * MCP4151 Library for Arduino
 * v1.0
 * MIT License
 * (c) 2022 Nathan "nwb99" Barnett
 */

#ifndef MCP4151_H
#define MCP4151_H

class MCP4151 
{
public:
    MCP4151(const int& CS, const int& MOSI, const int& MISO, const int& SCK, 
                const uint32_t& maxSpeedRead, const uint32_t& maxSpeedWrite, 
                const uint8_t& SPIMode);

    MCP4151(const int& CS, const int& MOSI, const int& MISO, const int& SCK);

    void writeValue(const int& value);
    int getCurValue();

private:
    volatile unsigned char MSb;
    volatile unsigned char LSb;
    volatile unsigned char receivedValue;
    volatile unsigned char errorBit;
    int CSpin;
    int SCKpin;
    int MOSIpin;
    int MISOpin;
    uint32_t speedR;
    uint32_t speedW;
    uint8_t spimode;
};

#endif