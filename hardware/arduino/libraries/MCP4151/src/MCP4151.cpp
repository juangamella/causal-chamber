/*
 * MCP4151 Library for Arduino
 * v1.0
 * MIT License
 * (c) 2022 Nathan "nwb99" Barnett
 */

#include <Arduino.h>
#include <MCP4151.h>
#include <SPI.h>

#define MAX_SPEED_WRITE  4000000
#define MAX_SPEED_READ   250000

MCP4151::MCP4151(const int& CS, const int& MOSI, const int& MISO, const int& SCK, 
                const uint32_t& maxSpeedRead, const uint32_t& maxSpeedWrite, 
                const uint8_t& SPIMode) {
    CSpin = CS;
    MOSIpin = MOSI;
    MISOpin = MISO;
    SCKpin = SCK;
    speedW = maxSpeedWrite;
    speedR = maxSpeedRead;
    spimode = SPIMode;
    pinMode(CSpin, OUTPUT);
    pinMode(MOSIpin, OUTPUT);
    pinMode(MISOpin, INPUT_PULLUP);
    pinMode(SCKpin, OUTPUT);
    digitalWrite(MOSIpin, LOW);
    digitalWrite(SCKpin, LOW);

}

MCP4151::MCP4151(const int& CS, const int& MOSI, const int& MISO, const int& SCK) {
    CSpin = CS;
    MOSIpin = MOSI;
    MISOpin = MISO;
    SCKpin = SCK;
    speedW = MAX_SPEED_WRITE; // 4 MHz
    speedR = MAX_SPEED_READ;  // 250 kHz
    spimode = SPI_MODE0;
    pinMode(CSpin, OUTPUT);
    pinMode(MOSIpin, OUTPUT);
    pinMode(MISOpin, INPUT_PULLUP);
    pinMode(SCKpin, OUTPUT);
    digitalWrite(MOSIpin, LOW);
}

void MCP4151::writeValue(const int& value) {
    SPI.beginTransaction(SPISettings(speedW, MSBFIRST, spimode));
    digitalWrite(CSpin, LOW);
    MSb = 0x0; // 0b0000xx00 ; where x = 0, command bits for write
    LSb = value & 0xFF; // No value greater than 255 ; send 0x0 otherwise
    uint16_t transmission = MSb << 8 | LSb;
    SPI.transfer16(transmission);
    digitalWrite(CSpin, HIGH); // Disable chip select
    SPI.endTransaction();
}

int MCP4151::getCurValue() {
    SPI.beginTransaction(SPISettings(speedR, MSBFIRST, spimode));
    digitalWrite(CSpin, LOW);
    
    MSb = 0xC;  // 0b00001100 ; the first 4 bits are the address, the next 
                // 2 bits are the command (11, read), and the last 2 are insignificant

    LSb = 0xFF; // send all ones for the second half so MCP4151 doesn't get confused.
    uint16_t transmission = MSb << 8 | LSb;
    receivedValue = SPI.transfer16(transmission); // MCP4151 will send value back after 
                                                  // receiving the last byte (OxFF).
    digitalWrite(CSpin, HIGH);
    SPI.endTransaction();
    return receivedValue;
}