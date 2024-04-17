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


/********************************************************************/
/*                                                                  */
/*     Code for the arduino board controlling the light tunnel       */
/*                                                                  */
/********************************************************************/

/* ------------------------------------------------------------------- */
/* PIN DEFINITIONS */

#define PIN_MSR_LED 23
#define PIN_SET_LED 25
#define PIN_DEBUG_1 34
#define PIN_DEBUG_2 36
#define PIN_DEBUG_3 38

#define PIN_DISP_SEL 6

#define PIN_CAMERA 5

#define PIN_LED_SGN 11
#define PIN_LED_CURRENT A1
#define NUM_LEDS 37

#define PIN_POTI_A A0
#define PIN_POTI_B A3

#define PIN_V_BOARD A15
#define PIN_V_REGULATOR A14

#define PIN_MOTOR_1_STEP 8
#define PIN_MOTOR_1_DIR 7
#define PIN_MOTOR_1_SEL_0 45
#define PIN_MOTOR_1_SEL_1 47
#define PIN_MOTOR_1_SEL_2 49

#define PIN_MOTOR_2_STEP 10
#define PIN_MOTOR_2_DIR 9
#define PIN_MOTOR_2_SEL_0 44
#define PIN_MOTOR_2_SEL_1 46
#define PIN_MOTOR_2_SEL_2 48

#define STEP_SEL_0 HIGH
#define STEP_SEL_1 HIGH
#define STEP_SEL_2 LOW
#define TEETH_SMALL 25
#define TEETH_LARGE 50
#define MOTOR_STEPS 1600
#define MOTOR_DELAY 400

#define PIN_POT_11_CS 28
#define PIN_POT_12_CS 30
#define PIN_POT_21_CS 32
#define PIN_POT_22_CS 36
#define PIN_POT_31_CS 38
#define PIN_POT_32_CS 40

#define EEPROM_ADDR 0

/* ------------------------------------------------------------------- */
/* LIBRARIES */
#include <Arduino.h> // For I2C communication
#include <Wire.h> // For I2C communication

#include <MCP4151.h> // For digital potentiometers / rheostats
#include <TCA9548A.h> // For I2C Multiplexer/Hub
#include <FastLED.h> // For LED matrix

#include "utils.h"
#include "serial_comms.h"
#include "spectrum.h" // For the color spectrum to test the light source
#include "Si115X.h" // Modified sunlight sensor v2.0

#include <EEPROM.h> // To mark whether the board was succesfully reset


/* ------------------------------------------------------------------- */
/* HARDWARE FUNCTIONS: to control actuators and sensors */

/*----------------------------*/
/* Stepper motors */
 
struct Motor {
  int position;
  int pin_step;
  int pin_dir;
  int pin_sel_0;
  int pin_sel_1;
  int pin_sel_2;
  int pin_poti;
  int zero;
};

Motor motor_1 = {.position=0,
                 .pin_step=PIN_MOTOR_1_STEP,
                 .pin_dir=PIN_MOTOR_1_DIR,
                 .pin_sel_0=PIN_MOTOR_1_SEL_0,
                 .pin_sel_1=PIN_MOTOR_1_SEL_1,
                 .pin_sel_2=PIN_MOTOR_1_SEL_2,
                 .pin_poti=PIN_POTI_A,
                 .zero=507};
Motor motor_2 = {.position=0,
                 .pin_step=PIN_MOTOR_2_STEP,
                 .pin_dir=PIN_MOTOR_2_DIR,
                 .pin_sel_0=PIN_MOTOR_2_SEL_0,
                 .pin_sel_1=PIN_MOTOR_2_SEL_1,
                 .pin_sel_2=PIN_MOTOR_2_SEL_2,
                 .pin_poti=PIN_POTI_B,
                 .zero=512};


void setup_motor(Motor motor) {
  pinMode(motor.pin_poti, INPUT);
  pinMode(motor.pin_step,OUTPUT);
  pinMode(motor.pin_dir,OUTPUT);
  pinMode(motor.pin_sel_0,OUTPUT);
  pinMode(motor.pin_sel_1,OUTPUT);
  pinMode(motor.pin_sel_2,OUTPUT);
  digitalWrite(motor.pin_sel_0,STEP_SEL_0);
  digitalWrite(motor.pin_sel_1,STEP_SEL_1);
  digitalWrite(motor.pin_sel_2,STEP_SEL_2);
}

void reset_motor(Motor * motor) {
  analogReference(DEFAULT);
  int dist;
  do {
    dist = (*motor).zero - analogRead((*motor).pin_poti);
    move_motor(motor, (dist > 0) ? 1 : -1);
  } while (dist != 0);
  (*motor).position = 0;
}

#define LOWER_LIMIT 10
#define UPPER_LIMIT 1010
void move_motor(Motor *motor, int steps) {
  analogReference(DEFAULT);
  // Set motor direction based on sign of steps
  int dir = 0;
  if (steps < 0) {
    dir = -1;
    digitalWrite((*motor).pin_dir,LOW);
  } else {
    dir = 1;
    digitalWrite((*motor).pin_dir,HIGH);
  }
  // Move motor
  for(int i = 0; i < dir*steps; i++) {
    int pos = analogRead((*motor).pin_poti);
    if (pos < LOWER_LIMIT || pos > UPPER_LIMIT)
      fail("er05");
    digitalWrite((*motor).pin_step,HIGH) ; 
    delayMicroseconds(MOTOR_DELAY);
    digitalWrite((*motor).pin_step,LOW); 
    delayMicroseconds(MOTOR_DELAY);
  }
  (*motor).position = (*motor).position + steps;
}

void set_angle(Motor *motor, float angle) {
  float current_angle = ((float)(*motor).position / MOTOR_STEPS) * ((float)TEETH_SMALL / TEETH_LARGE) * 360.0;
  float distance = angle - current_angle;
  int steps = round(distance / 360.0 * TEETH_LARGE / TEETH_SMALL * MOTOR_STEPS);
  move_motor(motor, steps);
}

float read_angle(Motor motor) {
  return ((float)(motor).position / MOTOR_STEPS) * ((float)TEETH_SMALL / TEETH_LARGE) * 360.0;
}

/*----------------------------*/
/* Light sensors */
 
Si115X si1151; //Sunlight sensor v2.0
TCA9548A<TwoWire> TCA; // I2C Multiplexer/Hub

// Light sensor photodiode size and gain parameters
byte ir_diodes[3];
byte vis_diodes[3];
byte ir_gains[3];
byte vis_gains[3];

// I2C switch channel map
const uint8_t channels[3] = {TCA_CHANNEL_0, TCA_CHANNEL_1, TCA_CHANNEL_2};

void setup_light_sensor(uint8_t sensor){
  uint8_t channel = channels[sensor];
  TCA.openChannel(channel);
  start_si1151();
  TCA.closeChannel(channel);
}

LightReading read_light_sensor(uint8_t sensor) {
  uint8_t channel = channels[sensor];
  LightReading reading;
  TCA.openChannel(channel);
  reading = read_si1151();
  TCA.closeChannel(channel);
  return reading;
}

/* Select the photodiode used for measurement */
void set_ir_diode(uint8_t sensor, float value) {
  // Translate to the sensors registry (p. 42 of the datasheet)
  //   variable level -> ADCMUX value in Si1151
  if (value != 0 && value != 1 && value != 2) {
    fail("er03");
  } else {
    uint8_t channel = channels[sensor];
    byte diode = byte(int(value)); // 0 - small, 1 - medium, 2 - large
    ir_diodes[sensor] = diode;
    // Set diode
    TCA.openChannel(channel);
    si1151.param_set(Si115X::ADCCONFIG_0, diode);
    TCA.closeChannel(channel);
  }
}

void set_vis_diode(uint8_t sensor, float value) {
  // Translate to the sensors registry (p. 42 of the datasheet)
  //   variable level -> ADCMUX value in Si1151
  if (value != 0 && value != 1) {
    fail("er03");
  } else {
    uint8_t channel = channels[sensor];
    byte diode = byte(int(value));
    vis_diodes[sensor] = diode;
    byte adcmux = (diode == 0) ? 0b01011 : 0b01101; // small - large visible diodes
    // Set diode
    TCA.openChannel(channel);
    si1151.param_set(Si115X::ADCCONFIG_1, adcmux);
    TCA.closeChannel(channel);
  }
}

/* Set the hardware gain (ADC integration time) of the light sensor */
void set_ir_gain(uint8_t sensor, float value) {
  // Translate to the sensors registry (p. 42 of the datasheet)
  //   variable level -> ADCMUX value in Si1151
  if (value != 0 && value != 1 && value != 2 && value != 3) {
    fail("er03");
  } else {
    uint8_t channel = channels[sensor];
    byte gain = byte(int(value));
    ir_gains[sensor] = gain;
    // Set gain
    TCA.openChannel(channel);
    si1151.param_set(Si115X::ADCSENS_0, gain);
    TCA.closeChannel(channel);
  }
}

/* Set the hardware gain (ADC integration time) of the light sensor */
void set_vis_gain(uint8_t sensor, float value) {
  // Translate to the sensors registry (p. 42 of the datasheet)
  //   variable level -> ADCMUX value in Si1151
  if (value != 0 && value != 1 && value != 2 && value != 3) {
    fail("er03");
  } else {
    uint8_t channel = channels[sensor];
    byte gain = byte(int(value));
    vis_gains[sensor] = gain;
    // Set gain
    TCA.openChannel(channel);
    si1151.param_set(Si115X::ADCSENS_1, gain);
    TCA.closeChannel(channel);
  }
}

/* void get_info() { */
/*   uint8_t result; */

/*   result = si1151.read_register(Si115X::DEVICE_ADDRESS, Si115X::HOSTIN_0, 1); */
/*   Serial.print("  HOSTIN0: "); */
/*   Serial.println(result); */
  
/*   result = si1151.read_register(Si115X::DEVICE_ADDRESS, Si115X::RESPONSE_0, 1); */
/*   Serial.print("  RESPONSE0: "); */
/*   Serial.println(result); */

/*   result = si1151.read_register(Si115X::DEVICE_ADDRESS, Si115X::RESPONSE_1, 1); */
/*   Serial.print("  RESPONSE1: "); */
/*   Serial.println(result); */
/* } */

void start_si1151() {
  //Wire.begin();
  // Wire.setClock(400000);
  if (si1151.ReadByte(0x00) != 0x51) {
    fail("er99");
  }
  //Serial.println();
  //Serial.println("Starting Si1551");

  delay(100);
  // get_info();

  // Serial.println();

  // Serial.println();
  // Serial.println("  Changing CHAN_LIST to 1");

  si1151.param_set(Si115X::CHAN_LIST, 0b00000011);
  si1151.param_set(Si115X::ADCCONFIG_1, 0b01101);
  // get_info();
}

#define LIGHT_MEASUREMENT_DURATION 12500 // In microseconds, slightly longer than the total measurement time for the max hw_gain (4)
#define COUNTER_MAX 4294967295

LightReading read_si1151() {
  unsigned long start = micros();
  // To deal with the microseconds counter overflowing after 70 minutes
  unsigned long time_to_overflow = COUNTER_MAX - start;
  if (time_to_overflow < LIGHT_MEASUREMENT_DURATION) {
    delayMicroseconds(time_to_overflow + 100);
    start = micros();
  }
  // Ask sensor to perform a measurement and wait until it's ready
  si1151.send_command(Si115X::FORCE, true);
  int result = si1151.send_command(Si115X::FORCE, true);
  if (result != 0 && result != 3) // 3 means there was overflow - read anyway
    fail("er08", String(result));
  LightReading measurement = si1151.read_output();
  if (measurement.ok < 0)
    fail("er09", String(measurement.ok));
  while (micros() - start < LIGHT_MEASUREMENT_DURATION) {
    true;
  }
  return measurement;
}

/*----------------------------*/
/* Light source */
CRGB leds[NUM_LEDS]; // To store values of LEDs

void set_color(int r, int g, int b) {
  for(int i=0; i < NUM_LEDS; i++) {
    leds[i].setRGB(r,g,b);
  }
  FastLED.show();
}

void leds_cross() {
  word idx[13] = {0,5,11,18,25,31,36,3,7,12,24,29,33};
  set_color(0,0,0);
  for(int i=0; i < 13; i++) {
    leds[idx[i]].setRGB(255,0,0);
  }
  FastLED.show();
}

void test_leds() {
  set_color(0,0,0);
  /* delay(500); */
  /* for (int i=255; i > 0; i-=5) { */
  /*   set_color(i,i,i); */
  /* } */
  set_color(0,0,0);
  delay(200);
  set_color(255,0,0);
  delay(500);
  set_color(0,255,0);
  delay(500);
  set_color(0,0,255);
  delay(500);
  set_color(255,255,0);
  delay(500);
  set_color(255,0,255);
  delay(500);
  set_color(0,255,255);
  delay(500);
  set_color(255,255,255);
  delay(500);
  set_color(0,0,0);
  delay(500);
  /* for(int i=0; i<768; i++) { */
  /*   set_color(spectrum_r[i],spectrum_g[i],spectrum_b[i]); */
  /*   delay(10); */
  /* } */
  /* set_color(0,0,0); */
  /* delay(200); */
  /* for(int i=0; i<768; i++) {     */
  /*   set_color(spectrum_r[i]/255.0*100,spectrum_g[i]/255.0*100,spectrum_b[i]/255.0*100); */
  /* } */
  /* set_color(0,0,0); */
  /* delay(200); */
}

/*----------------------------*/
/* Camera */
bool camera_flag = false;
unsigned long last_shutter = 0;

#define LOW_DURATION 500
#define CAM_DELAY 1000
void take_picture() {  
  digitalWrite(PIN_CAMERA, HIGH);
  digitalWrite(PIN_CAMERA, LOW);
  delay(LOW_DURATION);
  digitalWrite(PIN_CAMERA, HIGH);
  delay(CAM_DELAY);
}

/*----------------------------*/
/* Rheostats */
MCP4151 pot_11(PIN_POT_11_CS, MOSI, MISO, SCK);
MCP4151 pot_12(PIN_POT_12_CS, MOSI, MISO, SCK);
MCP4151 pot_21(PIN_POT_21_CS, MOSI, MISO, SCK);
MCP4151 pot_22(PIN_POT_22_CS, MOSI, MISO, SCK);
MCP4151 pot_31(PIN_POT_31_CS, MOSI, MISO, SCK);
MCP4151 pot_32(PIN_POT_32_CS, MOSI, MISO, SCK);

byte setting_pot_11;
byte setting_pot_12;
byte setting_pot_21;
byte setting_pot_22;
byte setting_pot_31;
byte setting_pot_32;

void set_pot_11_level(float value){
  pot_11.writeValue(value);
  // setting_pot_1 = (byte) value;
  // delay(POT_DELAY);
}

void set_pot_12_level(float value){
  pot_12.writeValue(value);
  // setting_pot_1 = (byte) value;
  // delay(POT_DELAY);
}

void set_pot_21_level(float value){
  pot_21.writeValue(value);
  // setting_pot_2 = (byte) value;
  // delay(POT_DELAY);
}

void set_pot_22_level(float value){
  pot_22.writeValue(value);
  // setting_pot_2 = (byte) value;
  // delay(POT_DELAY);
}

void set_pot_31_level(float value){
  pot_31.writeValue(value);
  // setting_pot_3 = (byte) value;
  // delay(POT_DELAY);
}

void set_pot_32_level(float value){
  pot_32.writeValue(value);
  // setting_pot_3 = (byte) value;
  // delay(POT_DELAY);
}

/*----------------------------*/
/* Analog sensors */

unsigned int angle_1_oversampling = 1;
unsigned int angle_2_oversampling = 1;
unsigned int current_oversampling = 1;
uint8_t angle_1_reference = DEFAULT; // DEFAULT = 5V
uint8_t angle_2_reference = DEFAULT;
uint8_t current_reference = DEFAULT;

/*----------------------------*/
/* General chamber control */
bool intervention_flag;

/*-----------------------------------------------------------------------*/
/* CHAMBER CONFIGURATIONS */
/*   - variables (names & exogenous or not)
     - setter functions
     - take_measurements(...) function */

#define NA -9999

/* ---------------------------------------------------------------- */
/* Standard configuration */
/*   All manipulable variables are exogenous */

// List of variables that this board transmits through serial
#define CHAMBER_CONFIG "CHAMBER_CONFIG,standard"
#define VARIABLES_LIST "VARIABLES_LIST,counter,flag,intervention,red,green,blue,osr_c,v_c,current,pol_1,pol_2,osr_angle_1,osr_angle_2,v_angle_1,v_angle_2,angle_1,angle_2,ir_1,vis_1,ir_2,vis_2,ir_3,vis_3,l_11,l_12,l_21,l_22,l_31,l_32,diode_ir_1,diode_vis_1,diode_ir_2,diode_vis_2,diode_ir_3,diode_vis_3,t_ir_1,t_vis_1,t_ir_2,t_vis_2,t_ir_3,t_vis_3,camera,v_board,v_reg"
#define NO_VARIABLES 44

#define counter 0
#define flag 1
#define intervention 2
#define red 3
#define green 4
#define blue 5
#define osr_c 6
#define v_c 7
#define current 8
#define pol_1 9
#define pol_2 10
#define osr_angle_1 11
#define osr_angle_2 12
#define v_angle_1 13
#define v_angle_2 14
#define angle_1 15
#define angle_2 16
#define ir_1 17
#define vis_1 18
#define ir_2 19
#define vis_2 20
#define ir_3 21
#define vis_3 22
#define l_11 23
#define l_12 24
#define l_21 25
#define l_22 26
#define l_31 27
#define l_32 28
#define diode_ir_1 29
#define diode_vis_1 30
#define diode_ir_2 31
#define diode_vis_2 32
#define diode_ir_3 33
#define diode_vis_3 34
#define t_ir_1 35
#define t_vis_1 36
#define t_ir_2 37
#define t_vis_2 38
#define t_ir_3 39
#define t_vis_3 40
#define camera 41
#define v_board 42
#define v_reg 43

float variables[NO_VARIABLES];

bool exogenous[NO_VARIABLES] = {
                                false //counter
                                , true //flag
                                , false //intervention
                                , true //red
                                , true //green
                                , true //blue
                                , true //osr_c
                                , true //v_c
                                , false //current
                                , true //pol_1
                                , true //pol_2
                                , true //osr_angle_1
                                , true //osr_angle_2
                                , true //v_angle_1
                                , true //v_angle_2
                                , false //angle_1
                                , false //angle_2
                                , false //ir_1
                                , false //vis_1
                                , false //ir_2
                                , false //vis_2
                                , false //ir_3
                                , false //vis_3
                                , true //l_11
                                , true //l_12
                                , true //l_21
                                , true //l_22
                                , true //l_31
                                , true //l_32
                                , true //diode_ir_1
                                , true //diode_vis_1
                                , true //diode_ir_2
                                , true //diode_vis_2
                                , true //diode_ir_3
                                , true //diode_vis_3
                                , true //t_ir_1
                                , true //t_vis_1
                                , true //t_ir_2
                                , true //t_vis_2
                                , true //t_ir_3
                                , true //t_vis_3
                                , true //camera
                                , false //v_board
                                , false //v_reg
};

// counter and intervention are always set internally and they don't
// have a setter function

void set_flag(float value) {
  variables[flag] = value;
}

void set_red(float value) {
  // Check value
  if (value == NA && exogenous[red]) {
    fail("er42");
  } else if (value >= 0 && value <= 255) {
    variables[red] = value;
    // Physical effect
    set_color(variables[red], variables[green], variables[blue]);
  }
}

void set_green(float value) {
  // Check value
  if (value == NA && exogenous[green]) {
    fail("er42");
  } else if (value >= 0 && value <= 255) {
    variables[green] = value;
    // Physical effect
    set_color(variables[red], variables[green], variables[blue]);
  } else {
    fail("er03");
  }
}

void set_blue(float value) {
  // Check value
  if (value == NA && exogenous[blue]) {
    fail("er42");
  } else if (value >= 0 && value <= 255) {
    variables[blue] = value;
    // Physical effect
    set_color(variables[red], variables[green], variables[blue]);
  } else {
    fail("er03");
  }
}

void set_osr_c(float value) {
  // Check value
  if (value == NA && exogenous[osr_c]) {
    fail("er42");
  } else {
    set_oversampling(&current_oversampling, value); // Values are checked here
    variables[osr_c] = value;
  } 
}

void set_v_c(float value) {
  // Check value
  if (value == NA && exogenous[v_c]) {
    fail("er42");
  } else {
    set_reference_voltage(&current_reference,value);
    variables[v_c] = value;
  }
}

void set_osr_angle_1(float value) {
  // Check value
  if (value == NA && exogenous[osr_angle_1]) {
    fail("er42");
  } else {
    set_oversampling(&angle_1_oversampling, value); // Values are checked here
    variables[osr_angle_1] = value;
  }
}

void set_v_angle_1(float value) {
  // Check value
  if (value == NA && exogenous[v_angle_1]) {
    fail("er42");
  } else {
    set_reference_voltage(&angle_1_reference,value);
    variables[v_angle_1] = value;
  }
}

void set_osr_angle_2(float value) {
  // Check value
  if (value == NA && exogenous[osr_angle_2]) {
    fail("er42");
  } else {
    set_oversampling(&angle_2_oversampling, value); // Values are checked here
    variables[osr_angle_2] = value;
  }
}

void set_v_angle_2(float value) {
  // Check value
  if (value == NA && exogenous[v_angle_2]) {
    fail("er42");
  } else {
    set_reference_voltage(&angle_2_reference,value);
    variables[v_angle_2] = value;
  }
}

void set_current(float value) {
  // Check value
  if (value == NA && exogenous[current]) {
    fail("er42");
  } else {
    variables[current] = value;
  }
}

void set_pol_1(float value) {
  // Check value
  if (value == NA && exogenous[pol_1]) {
    fail("er42");
  } else if (value >= -180 && value <= 180) {
    variables[pol_1] = value;
    // Physical effect
    set_angle(&motor_1, value);
  } else {
    fail("er03");
  }
}

void set_pol_2(float value) {
  // Check value
  if (value == NA && exogenous[pol_2]) {
    fail("er42");
  } else if (value >= -180 && value <= 180) {
    variables[pol_2] = value;
    // Physical effect
    set_angle(&motor_2, value);
  } else {
    fail("er03");
  }
}

void set_angle_1(float value) {
  // Check value
  if (value == NA && exogenous[angle_1]) {
    fail("er42");
  } else {
    variables[angle_1] = value;
  }
}

void set_angle_2(float value) {
  // Check value
  if (value == NA && exogenous[angle_2]) {
    fail("er42");
  } else {
    variables[angle_2] = value;
  }
}

void set_ir_1(float value) {
  // Check value
  if (value == NA && exogenous[ir_1]) {
    fail("er42");
  } else {
    variables[ir_1] = value;
  }
}

void set_vis_1(float value) {
  // Check value
  if (value == NA && exogenous[vis_1]) {
    fail("er42");
  } else {
    variables[vis_1] = value;
  }
}

void set_ir_2(float value) {
  // Check value
  if (value == NA && exogenous[ir_2]) {
    fail("er42");
  } else {
    variables[ir_2] = value;
  }
}

void set_vis_2(float value) {
  // Check value
  if (value == NA && exogenous[vis_2]) {
    fail("er42");
  } else {
    variables[vis_2] = value;
  }
}

void set_ir_3(float value) {
  // Check value
  if (value == NA && exogenous[ir_3]) {
    fail("er42");
  } else {
    variables[ir_3] = value;
  }
}

void set_vis_3(float value) {
  // Check value
  if (value == NA && exogenous[vis_3]) {
    fail("er42");
  } else {
    variables[vis_3] = value;
  }
}

void set_l_11(float value) {
  // Check value
  if (value == NA && exogenous[l_11]) {
    fail("er42");
  } else if (value >= 0 && value <= 255) {
    variables[l_11] = value;
    setting_pot_11 = 255 - value; // Physical effect
  } else {
    fail("er03");
  }
}

void set_l_12(float value) {
  // Check value
  if (value == NA && exogenous[l_12]) {
    fail("er42");
  } else if (value >= 0 && value <= 255) {
    variables[l_12] = value;
    setting_pot_12 = 255 - value; // Physical effect
  } else {
    fail("er03");
  }
}
 
void set_l_21(float value) {
  // Check value
  if (value == NA && exogenous[l_21]) {
    fail("er42");
  } else if (value >= 0 && value <= 255) {
    variables[l_21] = value;
    setting_pot_21 = 255 - value; // Physical effect
  } else {
    fail("er03");
  }
}

void set_l_22(float value) {
  // Check value
  if (value == NA && exogenous[l_22]) {
    fail("er42");
  } else if (value >= 0 && value <= 255) {
    variables[l_22] = value;
    setting_pot_22 = 255 - value; // Physical effect
  } else {
    fail("er03");
  }
}

void set_l_31(float value) {
  // Check value
  if (value == NA && exogenous[l_31]) {
    fail("er42");
  } else if (value >= 0 && value <= 255) {
    variables[l_31] = value;
    setting_pot_31 = 255 - value; // Physical effect
  } else {
    fail("er03");
  }
}

void set_l_32(float value) {
  // Check value
  if (value == NA && exogenous[l_32]) {
    fail("er42");
  } else if (value >= 0 && value <= 255) {
    variables[l_32] = value;
    setting_pot_32 = 255 - value; // Physical effect
  } else {
    fail("er03");
  }
}
  
void set_diode_ir_1(float value) {
  // Check value
  if (value == NA && exogenous[diode_ir_1]) {
    fail("er42");
  } else {
    set_ir_diode(0, value); // Physical effect - value checked in function
    variables[diode_ir_1] = value;
  }
}

void set_diode_vis_1(float value) {
  // Check value
  if (value == NA && exogenous[diode_vis_1]) {
    fail("er42");
  } else {
    set_vis_diode(0, value); // Physical effect - value checked in function
    variables[diode_vis_1] = value;
  }
}

void set_diode_ir_2(float value) {
  // Check value
  if (value == NA && exogenous[diode_ir_2]) {
    fail("er42");
  } else {
    set_ir_diode(1, value); // Physical effect - value checked in function
    variables[diode_ir_2] = value;
  }
}

void set_diode_vis_2(float value) {
  // Check value
  if (value == NA && exogenous[diode_vis_2]) {
    fail("er42");
  } else {
    set_vis_diode(1, value); // Physical effect - value checked in function
    variables[diode_vis_2] = value;
  }
}

void set_diode_ir_3(float value) {
  // Check value
  if (value == NA && exogenous[diode_ir_3]) {
    fail("er42");
  } else {
    set_ir_diode(2, value); // Physical effect - value checked in function
    variables[diode_ir_3] = value;
  }
}

void set_diode_vis_3(float value) {
  // Check value
  if (value == NA && exogenous[diode_vis_3]) {
    fail("er42");
  } else {
    set_vis_diode(2, value); // Physical effect - value checked in function
    variables[diode_vis_3] = value;
  }
}

void set_t_ir_1(float value) {
  // Check value
  if (value == NA && exogenous[t_ir_1]) {
    fail("er42");
  } else {
    set_ir_gain(0, value); // Physical effect - value checked in function
    variables[t_ir_1] = value;
  }
}

void set_t_vis_1(float value) {
  // Check value
  if (value == NA && exogenous[t_vis_1]) {
    fail("er42");
  } else {
    set_vis_gain(0, value); // Physical effect - value checked in function
    variables[t_vis_1] = value;
  }
}

void set_t_ir_2(float value) {
  // Check value
  if (value == NA && exogenous[t_ir_2]) {
    fail("er42");
  } else {
    set_ir_gain(1, value); // Physical effect - value checked in function
    variables[t_ir_2] = value;
  }
}

void set_t_vis_2(float value) {
  // Check value
  if (value == NA && exogenous[t_vis_2]) {
    fail("er42");
  } else {
    set_vis_gain(1, value); // Physical effect - value checked in function
    variables[t_vis_2] = value;
  }
}

void set_t_ir_3(float value) {
  // Check value
  if (value == NA && exogenous[t_ir_3]) {
    fail("er42");
  } else {
    set_ir_gain(2, value); // Physical effect - value checked in function
    variables[t_ir_3] = value;
  }
}

void set_t_vis_3(float value) {
  // Check value
  if (value == NA && exogenous[t_vis_3]) {
    fail("er42");
  } else {
    set_vis_gain(2, value); // Physical effect - value checked in function
    variables[t_vis_3] = value;
  }
}

void set_camera(float value) {
  if (value == NA && exogenous[camera])
    fail("er42");
  else if (value == 0 || value == 1) {
    variables[camera] = value;
    camera_flag = (value != 0);
  } else    
    fail("er03");
}

#define POT_DELAY 5
void take_measurements(float * measurements, float obs_counter) {
  // Chamber flags
  measurements[counter] = obs_counter;
  measurements[flag] = variables[flag];
  measurements[intervention] = intervention_flag;

  
  // Exogenous variables
  measurements[red] = variables[red];
  measurements[green] = variables[green];
  measurements[blue] = variables[blue];
  
  measurements[osr_c] = variables[osr_c];
  measurements[osr_angle_1] = angle_1_oversampling;
  measurements[osr_angle_2] = angle_2_oversampling;

  measurements[v_c] = variables[v_c];
  measurements[v_angle_1] = variables[v_angle_1];
  measurements[v_angle_2] = variables[v_angle_2];
  
  measurements[pol_1] = variables[pol_1];
  measurements[pol_2] = variables[pol_2];

  measurements[l_11] = variables[l_11];
  measurements[l_12] = variables[l_12];
  measurements[l_21] = variables[l_21];
  measurements[l_22] = variables[l_22];
  measurements[l_31] = variables[l_31];
  measurements[l_32] = variables[l_32];
  
  measurements[diode_ir_1] = variables[diode_ir_1];
  measurements[diode_ir_2] = variables[diode_ir_2];
  measurements[diode_ir_3] = variables[diode_ir_3];

  measurements[diode_vis_1] = variables[diode_vis_1];
  measurements[diode_vis_2] = variables[diode_vis_2];
  measurements[diode_vis_3] = variables[diode_vis_3];

  measurements[t_ir_1] = variables[t_ir_1];
  measurements[t_ir_2] = variables[t_ir_2];
  measurements[t_ir_3] = variables[t_ir_3];

  measurements[t_vis_1] = variables[t_vis_1];
  measurements[t_vis_2] = variables[t_vis_2];
  measurements[t_vis_3] = variables[t_vis_3];
  
  measurements[camera] = camera_flag;

  // Take sensor measurements  
  measurements[angle_1] = analog_avg(motor_1.pin_poti, angle_1_oversampling, angle_1_reference);
  measurements[angle_2] = analog_avg(motor_2.pin_poti, angle_2_oversampling, angle_2_reference);
  measurements[current] = analog_avg(PIN_LED_CURRENT, current_oversampling, current_reference);
  // Light sensor 1
  set_pot_11_level(setting_pot_11);
  set_pot_12_level(setting_pot_12);
  delay(POT_DELAY);
  LightReading reading = read_light_sensor(0);
  measurements[ir_1] = reading.ir;
  measurements[vis_1] = reading.vis;
  set_pot_11_level(255);
  set_pot_12_level(255);
  // Light sensor 2
  set_pot_21_level(setting_pot_21);
  set_pot_22_level(setting_pot_22);
  delay(POT_DELAY);
  reading = read_light_sensor(1);
  measurements[ir_2] = reading.ir;
  measurements[vis_2] = reading.vis;
  set_pot_21_level(255);
  set_pot_22_level(255);
  // Light sensor 3
  set_pot_31_level(setting_pot_31);
  set_pot_32_level(setting_pot_32);
  delay(POT_DELAY);
  reading = read_light_sensor(2);
  measurements[ir_3] = reading.ir;
  measurements[vis_3] = reading.vis;
  set_pot_31_level(255);
  set_pot_32_level(255);

  // Overwrite if sensor is intervened (i.e. variables[target] != NA)
  measurements[angle_1] = (variables[angle_1] == NA) ? measurements[angle_1] : variables[angle_1];
  measurements[angle_2] = (variables[angle_2] == NA) ? measurements[angle_2] : variables[angle_2];
  measurements[current] = (variables[current] == NA) ? measurements[current] : variables[current];
  measurements[ir_1] = (variables[ir_1] == NA) ? measurements[ir_1] : variables[ir_1];
  measurements[ir_2] = (variables[ir_2] == NA) ? measurements[ir_2] : variables[ir_2];
  measurements[ir_3] = (variables[ir_3] == NA) ? measurements[ir_3] : variables[ir_3];
  measurements[vis_1] = (variables[vis_1] == NA) ? measurements[vis_1] : variables[vis_1];
  measurements[vis_2] = (variables[vis_2] == NA) ? measurements[vis_2] : variables[vis_2];
  measurements[vis_3] = (variables[vis_3] == NA) ? measurements[vis_3] : variables[vis_3];
      
  // Board & regulator voltages for diagnosis
  measurements[v_board] = analogRead(PIN_V_BOARD);
  measurements[v_reg] = analogRead(PIN_V_REGULATOR);
}

/* ---------------------------------------------------------------- */
/* CHAMBER MAIN LOOP */

/* Setup function: executed on power-up */
void setup() {
    
  // Set diagnostic leds
  digitalWrite(PIN_MSR_LED, HIGH);
  digitalWrite(PIN_SET_LED, HIGH);
  
  // Setup display
  setup_display();
  lcd.setRGB(32,32,32);
  print_top("Initializing");
  print_bottom("  display");

  // Set variable map
  for (int i; i < NO_VARIABLES; i++)
    variables[i] = NA;
  
  print_bottom("  LEDs");
  FastLED.addLeds<NEOPIXEL, PIN_LED_SGN>(leds, NUM_LEDS);
  // test_leds();
  leds_cross();
  /* set_color(32,200,180); */
  pinMode(PIN_LED_CURRENT, INPUT);

  // Setup voltage meters
  print_bottom("  voltmeters");
  pinMode(PIN_V_BOARD, INPUT);
  pinMode(PIN_V_REGULATOR, INPUT);

  // Setup rheostats
  pinMode(53, OUTPUT);
  print_bottom("  rheostats");
  set_l_11(0);
  set_l_12(0);
  set_l_21(0);
  set_l_22(0);
  set_l_31(0);
  set_l_32(0);
  set_pot_11_level(255);
  set_pot_12_level(255);
  set_pot_21_level(255);
  set_pot_22_level(255);
  set_pot_31_level(255);
  set_pot_32_level(255);

  // Set up I2C Multiplexer (Hub)
  print_bottom("  multiplexer");
  TCA.begin(Wire);

  // Set up sunlight sensors
  print_bottom("  light sensors");
  byte DEFAULT_IR_DIODE = 2; // Large IR diode
  byte DEFAULT_VIS_DIODE = 1; // Large vis diodes
  byte DEFAULT_GAIN = 3; // out of 0-4

  setup_light_sensor(0);
  set_diode_ir_1(DEFAULT_IR_DIODE);
  set_diode_vis_1(DEFAULT_VIS_DIODE);
  set_t_ir_1(DEFAULT_GAIN);
  set_t_vis_1(DEFAULT_GAIN);

  setup_light_sensor(1);
  set_diode_ir_2(DEFAULT_IR_DIODE);
  set_diode_vis_2(DEFAULT_VIS_DIODE);
  set_t_ir_2(DEFAULT_GAIN);
  set_t_vis_2(DEFAULT_GAIN);

  setup_light_sensor(2);
  set_diode_ir_3(DEFAULT_IR_DIODE);
  set_diode_vis_3(DEFAULT_VIS_DIODE);
  set_t_ir_3(DEFAULT_GAIN);
  set_t_vis_3(DEFAULT_GAIN);
  
  // Setup polarizers
  print_bottom("  motors");
  setup_motor(motor_1);
  setup_motor(motor_2);
  reset_motor(&motor_1);
  reset_motor(&motor_2);
  set_pol_1(0);
  set_pol_2(0);
  /* // Only reset the motors if the board crashed or was not reset */
  /* // properly */
  /* if (EEPROM.read(EEPROM_ADDR)) { */
  /*   Serial.println("MOK"); */
  /*   EEPROM.write(EEPROM_ADDR, 0); */
  /* } else { */
  /*   Serial.println("MNOK"); */
  /*   reset_motor(&motor_1); */
  /*   reset_motor(&motor_2); */
  /* } */

  // Setup camera
  pinMode(PIN_CAMERA, OUTPUT);
  print_bottom("  camera");
  digitalWrite(PIN_CAMERA, HIGH);

  // Start serial port and wait for it to become available
  print_bottom("  connection");
  Serial.begin(500000);
  lcd.setRGB(32,128,32);
  print_top("Tunnel ready");
  clear_bottom();
  // Turn off diagnostic leds
  digitalWrite(PIN_MSR_LED, LOW);
  digitalWrite(PIN_SET_LED, LOW);

  // Await connection
  delay(500);
  send_string(CHAMBER_CONFIG);
  send_string(VARIABLES_LIST);
  print_top("Tunnel OK");
  
}

void(* resetFunc) (void) = 0; // To reset the board


/* Main loop: wait for an instruction, carry it out */

float observation_counter = 0.0; // To number all observations produced by the chamber
const float max_counter = 100000.0;

void loop() {
    // Read and decode an instruction from serial
  String msg = receive_string();
  Instruction instruction = decode_instruction(msg);

  /* MEASURE INSTRUCTION */
  if (instruction.type == MSR) {
    // Reply correct parsing
    int n = (int)instruction.p1;
    int wait = (int) instruction.p2;
    send_string(String("OK,MSR,n=" + String(n) + ",wait=" + String(wait)));
    
    // Take and transmit measurements
    for(int i=0; i <n; i++){
      digitalWrite(PIN_MSR_LED, HIGH); // While reading, LED is on
      if (camera_flag)
        take_picture();
      float measurements[NO_VARIABLES] = {NA};
      take_measurements(measurements, observation_counter);
      intervention_flag = false;
      observation_counter = observation_counter < max_counter ? observation_counter + 1.0 : 0.0;
      digitalWrite(PIN_MSR_LED, LOW); // While reading, LED is on
      // Send data back
      send_data((byte *) &measurements, sizeof(measurements));
    }
    send_string(String("OK,DONE"));
      
    /* SET INSTRUCTION */
  } else if (instruction.type == SET) {
    digitalWrite(PIN_SET_LED, HIGH);
    float value = instruction.p2;
    if (instruction.target.equals("flag"))
      set_flag(value);
    else if (instruction.target.equals("red"))
      set_red(value);
    else if (instruction.target.equals("green"))
      set_green(value);
    else if (instruction.target.equals("blue"))
      set_blue(value);
    else if (instruction.target.equals("osr_c"))
      set_osr_c(value);
    else if (instruction.target.equals("v_c"))
      set_v_c(value);
    else if (instruction.target.equals("current"))
      set_current(value);
    else if (instruction.target.equals("pol_1"))
      set_pol_1(value);
    else if (instruction.target.equals("pol_2"))
      set_pol_2(value);
    else if (instruction.target.equals("osr_angle_1"))
      set_osr_angle_1(value);
    else if (instruction.target.equals("osr_angle_2"))
      set_osr_angle_2(value);
    else if (instruction.target.equals("v_angle_1"))
      set_v_angle_1(value);
    else if (instruction.target.equals("v_angle_2"))
      set_v_angle_2(value);
    else if (instruction.target.equals("angle_1"))
      set_angle_1(value);
    else if (instruction.target.equals("angle_2"))
      set_angle_2(value);
    else if (instruction.target.equals("ir_1"))
      set_ir_1(value);
    else if (instruction.target.equals("vis_1"))
      set_vis_1(value);
    else if (instruction.target.equals("ir_2"))
      set_ir_2(value);
    else if (instruction.target.equals("vis_2"))
      set_vis_2(value);
    else if (instruction.target.equals("ir_3"))
      set_ir_3(value);
    else if (instruction.target.equals("vis_3"))
      set_vis_3(value);
    else if (instruction.target.equals("l_11"))
      set_l_11(value);
    else if (instruction.target.equals("l_12"))
      set_l_12(value);
    else if (instruction.target.equals("l_21"))
      set_l_21(value);
    else if (instruction.target.equals("l_22"))
      set_l_22(value);
    else if (instruction.target.equals("l_31"))
      set_l_31(value);
    else if (instruction.target.equals("l_32"))
      set_l_32(value);
    else if (instruction.target.equals("diode_ir_1"))
      set_diode_ir_1(value);
    else if (instruction.target.equals("diode_vis_1"))
      set_diode_vis_1(value);
    else if (instruction.target.equals("diode_ir_2"))
      set_diode_ir_2(value);
    else if (instruction.target.equals("diode_vis_2"))
      set_diode_vis_2(value);
    else if (instruction.target.equals("diode_ir_3"))
      set_diode_ir_3(value);
    else if (instruction.target.equals("diode_vis_3"))
      set_diode_vis_3(value);
    else if (instruction.target.equals("t_ir_1"))
      set_t_ir_1(value);
    else if (instruction.target.equals("t_vis_1"))
      set_t_vis_1(value);
    else if (instruction.target.equals("t_ir_2"))
      set_t_ir_2(value);
    else if (instruction.target.equals("t_vis_2"))
      set_t_vis_2(value);
    else if (instruction.target.equals("t_ir_3"))
      set_t_ir_3(value);
    else if (instruction.target.equals("t_vis_3"))
      set_t_vis_3(value);
    else if (instruction.target.equals("camera"))
      set_camera(value);
    else
      fail("er04", instruction.target);
    // Send reply
    intervention_flag = true;
    send_string(String("OK,SET," + instruction.target + "=" + String(value)));
    digitalWrite(PIN_SET_LED, LOW);

    /* RESET INSTRUCTION */
  } else if (instruction.type == RST) {
    digitalWrite(PIN_SET_LED, HIGH);
    digitalWrite(PIN_MSR_LED, HIGH);
    set_angle(&motor_1, 0);
    set_angle(&motor_2, 0);
    // EEPROM.write(EEPROM_ADDR, 1);
    send_string(String("OK,RST"));
    resetFunc();
      
    /* UNKNOWN INSTRUCTION */
  } else
    fail("er01",msg);
}


