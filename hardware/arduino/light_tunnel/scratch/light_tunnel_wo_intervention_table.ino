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
/*     Code for the arduino board controlling the wind tunnel       */
/*                                                                  */
/********************************************************************/

// ----------------------------------------------------------------
// Pin definitions

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
/* Libraries */
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
/* Global variables & macros */
#define NA -9999

// List of variables that this board transmits through serial
#define CHAMBER_CONFIG "CHAMBER_CONFIG,standard"
#define VARIABLES_LIST "VARIABLES_LIST,counter,flag,intervention,red,green,blue,osr_c,v_c,current,pol_1,pol_2,osr_angle_1,osr_angle_2,v_angle_1,v_angle_2,angle_1,angle_2,ir_1,vis_1,ir_2,vis_2,ir_3,vis_3,l_11,l_12,l_21,l_22,l_31,l_32,diode_ir_1,diode_vis_1,diode_ir_2,diode_vis_2,diode_ir_3,diode_vis_3,t_ir_1,t_vis_1,t_ir_2,t_vis_2,t_ir_3,t_vis_3,camera,v_board,v_reg"
#define NO_VARIABLES 44

/* ------------------------------------------------------------------- */
/* Initializations */

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

Si115X si1151; //Sunlight sensor v2.0
TCA9548A<TwoWire> TCA; // I2C Multiplexer/Hub

// Light sensor photodiode size and gain parameters
byte ir_diodes[3];
byte vis_diodes[3];
byte ir_gains[3];
byte vis_gains[3];

float flag;

CRGB leds[NUM_LEDS]; // To store values of LEDs

// light-source levels
int red = 0;
int green = 0;
int blue = 0;

bool camera = false;
unsigned long last_shutter = 0;

bool intervention_flag;

// Rheostat settings
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

// Oversampling rate for analog sensors
unsigned int angle_1_oversampling = 1;
unsigned int angle_2_oversampling = 1;
unsigned int current_oversampling = 1;
// Reference voltage for analog sensors
uint8_t angle_1_reference = DEFAULT; // DEFAULT = 5V
uint8_t angle_2_reference = DEFAULT;
uint8_t current_reference = DEFAULT;

/* ---------------------------------------------------------------- */
/* Setup function */

void setup() {

  // Set diagnostic leds
  digitalWrite(PIN_MSR_LED, HIGH);
  digitalWrite(PIN_SET_LED, HIGH);
  
  // Setup display
  setup_display();
  lcd.setRGB(32,32,32);
  print_top("Initializing");
  print_bottom("  display");
    
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
  setting_pot_11 = 255;
  setting_pot_12 = 255;
  setting_pot_21 = 255;
  setting_pot_22 = 255;
  setting_pot_31 = 255;
  setting_pot_32 = 255;
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
  set_ir_diode(0, DEFAULT_IR_DIODE);
  set_vis_diode(0, DEFAULT_VIS_DIODE);
  set_ir_gain(0, DEFAULT_GAIN);
  set_vis_gain(0, DEFAULT_GAIN);

  setup_light_sensor(1);
  set_ir_diode(1, DEFAULT_IR_DIODE);
  set_vis_diode(1, DEFAULT_VIS_DIODE);
  set_ir_gain(1, DEFAULT_GAIN);
  set_vis_gain(1, DEFAULT_GAIN);

  setup_light_sensor(2);
  set_ir_diode(2, DEFAULT_IR_DIODE);
  set_vis_diode(2, DEFAULT_VIS_DIODE);
  set_ir_gain(2, DEFAULT_GAIN);
  set_vis_gain(2, DEFAULT_GAIN);
  
  // Setup motors
  print_bottom("  motors");
  setup_motor(motor_1);
  setup_motor(motor_2);
  reset_motor(&motor_1);
  reset_motor(&motor_2);
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


// ----------------------------------------------------------------
// Main loop

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
      if (camera)
        take_picture();
      float variables[NO_VARIABLES] = {NA}; // counter + sensor readings
      take_measurements(variables, observation_counter);
      intervention_flag = false;
      observation_counter = observation_counter < max_counter ? observation_counter + 1.0 : 0.0;
      digitalWrite(PIN_MSR_LED, LOW); // While reading, LED is on
      // Send data back
      send_data((byte *) &variables, sizeof(variables));
    }
    send_string(String("OK,DONE"));
      
    /* SET INSTRUCTION */
  } else if (instruction.type == SET) {
    digitalWrite(PIN_SET_LED, HIGH);
    float value = instruction.p2;
    if (instruction.target.equals("flag"))
      flag = value;
    else if (instruction.target.equals("red"))
      (value >= 0 && value <= 255) ? set_color(value, green, blue) : fail("er03");        
    else if (instruction.target.equals("green"))
      (value >= 0 && value <= 255) ? set_color(red, value, blue) : fail("er03");
    else if (instruction.target.equals("blue"))
      (value >= 0 && value <= 255) ? set_color(red, green, value) : fail("er03");
    else if (instruction.target.equals("pol_1"))
      set_angle(&motor_1, value);
    else if (instruction.target.equals("pol_2"))
      set_angle(&motor_2, value);
    else if (instruction.target.equals("camera"))
      camera = (bool) value;
    else if (instruction.target.equals("l_11")) {
      if (value >= 0 && value <= 255)
        setting_pot_11 = 255 - value; // Full LED brightness (255) -> 0 rheostat resistance
      else
        fail("er03");
    }
    else if (instruction.target.equals("l_12")) {
      if (value >= 0 && value <= 255)
        setting_pot_12 = 255 - value;
      else
        fail("er03");
    }
    else if (instruction.target.equals("l_21")) {
      if (value >= 0 && value <= 255)
        setting_pot_21 = 255 - value;
      else
        fail("er03");
    }
    else if (instruction.target.equals("l_22")) {
      if (value >= 0 && value <= 255)
        setting_pot_22 = 255 - value;
      else
        fail("er03");
    }
    else if (instruction.target.equals("l_31")) {
      if (value >= 0 && value <= 255)
        setting_pot_31 = 255 - value;
      else
        fail("er03");
    }
    else if (instruction.target.equals("l_32")) {
      if (value >= 0 && value <= 255)
        setting_pot_32 = 255 - value;
      else
        fail("er03");
    }
    // Light-sensor diodes
    else if (instruction.target.equals("diode_ir_1"))
      set_ir_diode(0, value);
    else if (instruction.target.equals("diode_vis_1"))
      set_vis_diode(0, value);
    else if (instruction.target.equals("diode_ir_2"))
      set_ir_diode(1, value);
    else if (instruction.target.equals("diode_vis_2"))
      set_vis_diode(1, value);
    else if (instruction.target.equals("diode_ir_3"))
      set_ir_diode(2, value);
    else if (instruction.target.equals("diode_vis_3"))
      set_vis_diode(2, value);
    // Light-sensor exposures (hardware gain)
    else if (instruction.target.equals("t_ir_1"))
      set_ir_gain(0, value);
    else if (instruction.target.equals("t_vis_1"))
      set_vis_gain(0, value);
    else if (instruction.target.equals("t_ir_2"))
      set_ir_gain(1, value);
    else if (instruction.target.equals("t_vis_2"))
      set_vis_gain(1, value);
    else if (instruction.target.equals("t_ir_3"))
      set_ir_gain(2, value);
    else if (instruction.target.equals("t_vis_3"))
      set_vis_gain(2, value);
    // Oversampling rates
    else if (instruction.target.equals("osr_c"))
        set_oversampling(&current_oversampling, value);
    else if (instruction.target.equals("osr_angle_1"))
        set_oversampling(&angle_1_oversampling, value);
    else if (instruction.target.equals("osr_angle_2"))
        set_oversampling(&angle_2_oversampling, value);
    // Reference voltages
    else if (instruction.target.equals("v_c"))
      set_reference_voltage(&current_reference,value);
    else if (instruction.target.equals("v_angle_1"))
      set_reference_voltage(&angle_1_reference,value);
    else if (instruction.target.equals("v_angle_2"))
      set_reference_voltage(&angle_2_reference,value);
    else
      fail("er04", msg);
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

/*-----------------------------------------------------------------------*/
/* Camera */

#define LOW_DURATION 500
#define CAM_DELAY 1000
void take_picture() {  
  digitalWrite(PIN_CAMERA, HIGH);
  digitalWrite(PIN_CAMERA, LOW);
  delay(LOW_DURATION);
  digitalWrite(PIN_CAMERA, HIGH);
  delay(CAM_DELAY);
}

/*-----------------------------------------------------------------------*/
/* Sunlight sensors */

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


/*   byte adcmux; */
/*   if (diode == 0) */
/*     adcmux = 0x0; // Small IR diode */
/*   else if (diode == 1) */
/*     adcmux = 0x1; // Medium IR diode */
/*   else if (diode == 2) */
/*     adcmux = 0x2; // Large IR diode */
/*   else if (diode == 3) */
/*     adcmux = 0b01011; // Small visible diode */
/*   else if (diode == 4) */
/*     adcmux = 0b01101; // Large visible diode */
/*   else */
/*     fail("er96"); */
  
/*   // Send instruction to Si1151 */
/*   if (sensor == 1) { */
/*     diode_1 = diode; */
/*     TCA.openChannel(TCA_CHANNEL_0); */
/*     si1151.param_set(Si115X::ADCCONFIG_0, adcmux); */
/*     TCA.closeChannel(TCA_CHANNEL_0); */
/*   } else if (sensor == 2) { */
/*     diode_2 = diode; */
/*     TCA.openChannel(TCA_CHANNEL_1); */
/*     si1151.param_set(Si115X::ADCCONFIG_0, adcmux); */
/*     TCA.closeChannel(TCA_CHANNEL_1); */
/*   } else if (sensor == 3) { */
/*     diode_3 = diode; */
/*     TCA.openChannel(TCA_CHANNEL_2); */
/*     si1151.param_set(Si115X::ADCCONFIG_0, adcmux); */
/*     TCA.closeChannel(TCA_CHANNEL_2); */
/*   } else { */
/*     fail("er97"); */
/*   } */
/* } */

/* /\* Set the hardware gain (ADC integration time) of the light sensor *\/ */
/* void set_sensor_gain(uint8_t sensor, float gain) { */
/*   // Check within range */
/*   if (gain < 0 || gain > 11) */
/*     fail("er95"); */
/*   byte reg = byte(int(gain)); */
/*   // Send instruction to Si1151 */
/*   if (sensor == 1) { */
/*     gain_1 = gain; */
/*     TCA.openChannel(TCA_CHANNEL_0); */
/*     si1151.param_set(Si115X::ADCSENS_0, gain); */
/*     TCA.closeChannel(TCA_CHANNEL_0); */
/*   } else if (sensor == 2) { */
/*     gain_2 = gain; */
/*     TCA.openChannel(TCA_CHANNEL_1); */
/*     si1151.param_set(Si115X::ADCSENS_0, gain); */
/*     TCA.closeChannel(TCA_CHANNEL_1); */
/*   } else if (sensor == 3) { */
/*     gain_3 = gain; */
/*     TCA.openChannel(TCA_CHANNEL_2); */
/*     si1151.param_set(Si115X::ADCSENS_0, gain); */
/*     TCA.closeChannel(TCA_CHANNEL_2); */
/*   } else { */
/*     fail("er94"); */
/*   } */
/* } */

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


/* float read_si1151() { */
/*   // Ask sensor to perform a measurement and wait until it's ready */
/*   si1151.send_command(Si115X::FORCE, true); */
/*   int result = si1151.send_command(Si115X::FORCE, true); */
/*   if (result != 0 && result != 3) // 3 means there was overflow - read anyway */
/*     fail("er08", String(result)); */
/*   float measurement = si1151.read_output(); */
/*   if (measurement < 0) */
/*     fail("er09", String(measurement)); */
/*   return measurement; */
/* } */

/*-----------------------------------------------------------------------*/
/* Stepper motors */

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

/*-----------------------------------------------------------------------*/
/* Potentiometers */

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

/*-----------------------------------------------------------------------*/
/* Light source */

void set_color(int r, int g, int b) {
  for(int i=0; i < NUM_LEDS; i++) {
    leds[i].setRGB(r,g,b);
  }
  FastLED.show();
  red = r;
  green = g;
  blue = b;
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

/* ---------------------------------------------------------------- */
/* CHAMBER CONFIGURATIONS */

/* Standard configuration */
/*   All manipulable variables are exogenous */
#define POT_DELAY 5
void take_measurements(float * variables, float counter) {
  variables[0] = counter;
  variables[1] = flag;
  variables[2] = intervention_flag;
  // Light source
  variables[3] = red;
  variables[4] = green;
  variables[5] = blue;
  variables[6] = current_oversampling;
  variables[7] = get_reference_voltage(&current_reference);
  // Current
  variables[8] = analog_avg(PIN_LED_CURRENT, current_oversampling, current_reference);
  // Polarizer motors & angles
  variables[9] = read_angle(motor_1);
  variables[10] = read_angle(motor_2);
  variables[11] = angle_1_oversampling;
  variables[12] = angle_2_oversampling;
  variables[13] = get_reference_voltage(&angle_1_reference);
  variables[14] = get_reference_voltage(&angle_2_reference);
  variables[15] = analog_avg(motor_1.pin_poti, angle_1_oversampling, angle_1_reference);
  variables[16] = analog_avg(motor_2.pin_poti, angle_2_oversampling, angle_2_reference);
  // Light sensor 1
  set_pot_11_level(setting_pot_11);
  set_pot_12_level(setting_pot_12);
  delay(POT_DELAY);
  LightReading reading = read_light_sensor(0);
  variables[17] = reading.ir;
  variables[18] = reading.vis;
  set_pot_11_level(255);
  set_pot_12_level(255);
  // Light sensor 2
  set_pot_21_level(setting_pot_21);
  set_pot_22_level(setting_pot_22);
  delay(POT_DELAY);
  reading = read_light_sensor(1);
  variables[19] = reading.ir;
  variables[20] = reading.vis;
  set_pot_21_level(255);
  set_pot_22_level(255);
  // Light sensor 3
  set_pot_31_level(setting_pot_31);
  set_pot_32_level(setting_pot_32);
  delay(POT_DELAY);
  reading = read_light_sensor(2);
  variables[21] = reading.ir;
  variables[22] = reading.vis;
  set_pot_31_level(255);
  set_pot_32_level(255);
  // Rheostats
  variables[23] = 255 - setting_pot_11;
  variables[24] = 255 - setting_pot_12;
  variables[25] = 255 - setting_pot_21;
  variables[26] = 255 - setting_pot_22;
  variables[27] = 255 - setting_pot_31;
  variables[28] = 255 - setting_pot_32;
  // Sensor photodiodes
  variables[29] = ir_diodes[0];
  variables[30] = vis_diodes[0];
  variables[31] = ir_diodes[1];
  variables[32] = vis_diodes[1];
  variables[33] = ir_diodes[2];
  variables[34] = vis_diodes[2];
  // Sensor gains
  variables[35] = ir_gains[0];
  variables[36] = vis_gains[0];
  variables[37] = ir_gains[1];
  variables[38] = vis_gains[1];
  variables[39] = ir_gains[2];
  variables[40] = vis_gains[2];
  // Camera setting (if 1, send trigger signal on camera pins)
  variables[41] = camera;
  // Board & regulator voltages for diagnosis
  variables[42] = analogRead(PIN_V_BOARD);
  variables[43] = analogRead(PIN_V_REGULATOR);
}
