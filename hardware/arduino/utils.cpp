/* ; -*- mode: C;-*-

   MIT License

   Copyright (c) 2023 Juan L. Gamella

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in all
   copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
   SOFTWARE.
*/

#include <Arduino.h>
#include "utils.h"
#include "rgb_lcd.h" // For RGB display

/*-----------------------------------------------------------------------*/
/* Analog sensors: microphone, amplification signals, current */
#define MAX_ANALOG_SAMPLES 8

void set_oversampling(unsigned int * setting, float value) {
  if (value == 1 || value == 2 || value == 4 || value == 8)
    *setting = (unsigned int) value;
  else
    fail("er03");
}

void set_reference_voltage(uint8_t * setting, float value) {
  if (value == 5.0)
    *setting = DEFAULT;
  else if (value == 2.56)
    *setting = INTERNAL2V56;
  else if (value == 1.1)
    *setting = INTERNAL1V1;
  else
    fail("er03");
}

float get_reference_voltage(uint8_t * setting) {
  float voltage;
  if (*setting == DEFAULT)
    voltage = 5.0;
  else if (*setting == INTERNAL2V56)
    voltage = 2.56;
  else if (*setting == INTERNAL1V1)
    voltage = 1.1;
  return voltage;
}

float analog_avg(int pin, int samples, uint8_t reference) {
  // Set new analog reference; discard first measurement and wait so
  // the ADC reading has adjusted (see page 275 of the atmega2560
  // datasheet :
  // https://ww1.microchip.com/downloads/en/devicedoc/atmel-2549-8-bit-avr-microcontroller-atmega640-1280-1281-2560-2561_datasheet.pdf)
  analogReference(reference); 
  analogRead(pin);
  delay(5); // 4 milliseconds was too little (ADC needed didn't have time to reset); 5 was enough
  // Take measurements
  float avg = 0;
  float discard = 0;
  for (int i=0; i<MAX_ANALOG_SAMPLES; i++) {
    if (i % (MAX_ANALOG_SAMPLES / samples) == 0)
      avg += (float)analogRead(pin);
    else
      discard += (float)analogRead(pin);
  }
  return avg / samples;
}

/* ------------------------------------------------------------------- */
/* Instruction parser */

/* Decode an instruction */
Instruction decode_instruction(String instruction) {
  Instruction result;
  if (instruction.startsWith("RST")) {
    result.type = RST;
    return result;
  }
  // Check correct number of parameters and recognized instruction
  int n_params = 0;
  for (int i=0; i < instruction.length(); i++) {
    if (instruction.charAt(i) == ',')
      n_params++;
  }
  if (n_params != 2) {
    result.type = UNK;
    return result;
  } else if (instruction.startsWith("MSR,"))
    result.type = MSR;
  else if (instruction.startsWith("SET,"))
    result.type = SET;
  else {
    result.type = UNK;
    return result;
  }
  int start = instruction.indexOf(',');
  instruction.setCharAt(start, '.');
  int end = instruction.indexOf(',');
  result.p2 = instruction.substring(end+1).toFloat();
  if (result.type == SET)
    result.target = instruction.substring(start+1,end);
  else
    result.p1 = instruction.substring(start+1,end).toFloat();
  return result;
}

/* ------------------------------------------------------------------- */
/* LCD display */

rgb_lcd lcd; // RGB display

void setup_display() {
  lcd.begin(16, 2);
}

void set_display_color(byte red, byte green, byte blue) {
  lcd.setRGB(red,green,blue);
}

void clear_top() {
  lcd.setCursor(0,0);
  lcd.print("                ");
}

void clear_bottom() {
  lcd.setCursor(0,1);
  lcd.print("                ");
}

void print_top(String msg) {
  clear_top();
  lcd.setCursor(0,0);
  lcd.print(msg);
}

void print_bottom(String msg) {
  clear_bottom();
  lcd.setCursor(0,1);
  lcd.print(msg);
}

/* ------------------------------------------------------------------- */
/* Other auxiliary functions */

void fail( String msg){
  lcd.setRGB(64,64,64);
  clear_top();
  clear_bottom();
  print_top(msg);
  Serial.print(String("<ERR," + String(msg) + ">"));
  while(true);
}

void fail(String msg, String params){
  lcd.setRGB(64,64,64);
  clear_top();
  clear_bottom();
  print_top(msg);
  Serial.print(String("<ERR," + String(msg) + "," + String(params) + ">"));
  while(true);  
}
