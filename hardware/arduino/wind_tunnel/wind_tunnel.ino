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

/* ------------------------------------------------------------------- */
/* PIN DEFINITIONS */

#define PIN_MSR_LED 44
#define PIN_SET_LED 46
#define PIN_DEBUG_1 34

#define PIN_DISP_SEL 8

#define PIN_FAN_IN_PWM 11
#define PIN_FAN_IN_TACH 2
#define PIN_FAN_IN_CURRENT A3

#define PIN_FAN_OUT_PWM 12
#define PIN_FAN_OUT_TACH 3
#define PIN_FAN_OUT_CURRENT A2

#define PIN_POT_1_CS 32
#define PIN_POT_2_CS 30

#define PIN_STEP 10
#define PIN_DIR 9
#define PIN_SEL_0 7
#define PIN_SEL_1 6
#define PIN_SEL_2 5

#define PIN_NOISE 28

#define PIN_MIC A1
#define PIN_SGN_POT_1 A14
#define PIN_SGN_POT_2 A15

/* ------------------------------------------------------------------- */
/* LIBRARIES */

#include <Arduino.h>
#include <Wire.h> // For I2C communication

#include "utils.h"
#include "serial_comms.h"

#include <MCP4151.h> // For digital potentiometers
#include <TimerOne.h> // For PWM modulation of LEDs
#include "Dps310.h" // High-precision barometer
#include <TCA9548A.h> // For I2C Multiplexer/Hub
#include <Entropy.h> // for white noise generation using clock jitter

/* ------------------------------------------------------------------- */
/* HARDWARE FUNCTIONS: to control actuators and sensors */


// Struct definitions on top so compiler has them before prototypes:
// https://forum.arduino.cc/t/struct-not-defined-in-this-scope/66566

struct Motor {
  int position;
  int pin_step;
  int pin_dir;
  int pin_sel_0;
  int pin_sel_1;
  int pin_sel_2;
  bool sel_0;
  bool sel_1;
  bool sel_2;
  unsigned int steps;
  unsigned int delay;
  float ratio; // How many turns of the motor equals one turn of the actuator (~in polarizers TEETH_SMALL / TEETH_LARGE)
};

struct Fan {
  int pin_pwm;
  int pin_interrupt;
  float load;
  volatile int counter;
};

/*----------------------------*/
/* Hatch stepper motor */

Motor motor = {.position=0,
               .pin_step=PIN_STEP,
               .pin_dir=PIN_DIR,
               .pin_sel_0=PIN_SEL_0,
               .pin_sel_1=PIN_SEL_1,
               .pin_sel_2=PIN_SEL_2,
               .sel_0=1,
               .sel_1=1,
               .sel_2=1,
               .steps=3200,
               .delay=400,
               .ratio=1.0};

void setup_motor(Motor motor) {
  pinMode(motor.pin_step,OUTPUT);
  pinMode(motor.pin_dir,OUTPUT);
  pinMode(motor.pin_sel_0,OUTPUT);
  pinMode(motor.pin_sel_1,OUTPUT);
  pinMode(motor.pin_sel_2,OUTPUT);
  digitalWrite(motor.pin_sel_0,motor.sel_0);
  digitalWrite(motor.pin_sel_1,motor.sel_1);
  digitalWrite(motor.pin_sel_2,motor.sel_2);
}

void move_motor(Motor *motor, int steps) {
  // Set motor direction based on sign of steps
  int dir = 0;
  if (steps < 0) {
    dir = -1;
    digitalWrite((*motor).pin_dir,HIGH);
  } else {
    dir = 1;
    digitalWrite((*motor).pin_dir,LOW);
  }
  // Move motor
  for(int i = 0; i < dir*steps; i++) {
    digitalWrite((*motor).pin_step,HIGH); 
    delayMicroseconds((*motor).delay);
    digitalWrite((*motor).pin_step,LOW); 
    delayMicroseconds((*motor).delay);
  }
  (*motor).position = (*motor).position + steps;
}

void set_angle(Motor *motor, float angle) {
  float current_angle = ((float)(*motor).position / (*motor).steps) * (*motor).ratio * 360.0;
  float distance = angle - current_angle;
  int steps = round(distance / 360.0 / (*motor).ratio * (*motor).steps);
  move_motor(motor, steps);
}

float read_angle(Motor motor) {
  return ((float)motor.position / motor.steps) * motor.ratio * 360.0;
}


/*----------------------------*/
/* Fans */

volatile float rpm_in, rpm_out;



Fan fan_in = {.pin_pwm = PIN_FAN_IN_PWM, .pin_interrupt = PIN_FAN_IN_TACH, .load = 0, .counter = 0};
Fan fan_out = {.pin_pwm = PIN_FAN_OUT_PWM, .pin_interrupt = PIN_FAN_OUT_TACH, .load = 0, .counter = 0};

void setup_fans() {
  Timer1.initialize(40);
  Timer1.pwm(fan_in.pin_pwm, 0, 40);
  Timer1.pwm(fan_out.pin_pwm, 0, 40);
}

void set_fan_load(Fan * fan, float load) {
  Timer1.setPwmDuty((*fan).pin_pwm, round(1023*load));
  (*fan).load = load;
}

// Resolution for fan RPM (true = microseconds timer / false = milliseconds timer)
bool fan_in_high_res = true;
bool fan_out_high_res = true;

volatile unsigned long last_tick_in, last_tick_out;
volatile bool fan_in_last_res = true;
volatile bool fan_out_last_res = true;
#define DEBOUNCE_MICROS 5000
#define DEBOUNCE_MILLIS 5

/* About the debounce parameter: If the time difference between to */
/* ticks is below the debounce parameter, we assume the tick was due */
/* to noise in the system, as a 5 milliseconds the fan would be */
/* turning at 6K RPM, double of its max. rated speed. This also */
/* protects against negative differences after timer counter resets */
/* (~70 minutes for microseconds). The fan_*_last_res flags indicate */
/* with what resolution the last tick was measured, so only ticks with */
/* the same resolution are compared to compute the RPM. */


void tick_fan_in(){
  if (fan_in_high_res) {
    unsigned long now = micros();
    float diff = (float) now - (float) last_tick_in;
    last_tick_in = now;
    if (diff > DEBOUNCE_MICROS && fan_in_last_res) {
      rpm_in = 30000000 / diff;
    }
    fan_in_last_res = true;
  } else {
    unsigned long now = millis();
    float diff = (float) now - (float) last_tick_in;
    last_tick_in = now;
    if (diff > DEBOUNCE_MILLIS && !fan_in_last_res) {
      rpm_in = 30000 / diff;
    }
    fan_in_last_res = false;
  }
}

void tick_fan_out(){
  if (fan_out_high_res) {
    unsigned long now = micros();
    float diff = (float) now - (float) last_tick_out;
    last_tick_out = now;
    if (diff > DEBOUNCE_MICROS && fan_out_last_res) {
      rpm_out = 30000000 / diff;
    }
    fan_out_last_res = true;
  } else {
    unsigned long now = millis();
    float diff = (float) now - (float) last_tick_out;
    last_tick_out = now;
    if (diff > DEBOUNCE_MILLIS && !fan_out_last_res) {
      rpm_out = 30000 / diff;
    }
    fan_out_last_res = false;
  }
}

float get_rpm_in() {
  noInterrupts();
  float rpm = rpm_in;
  interrupts();
  return rpm;
}

float get_rpm_out() {
  noInterrupts();
  float rpm = rpm_out;
  interrupts();
  return rpm;
}


/*----------------------------*/
/* Barometers */

Dps310 barometer_upwind = Dps310();
Dps310 barometer_downwind = Dps310();
Dps310 barometer_ambient = Dps310();
Dps310 barometer_intake = Dps310();
TCA9548A<TwoWire> TCA; // I2C Multiplexer/Hub

// Oversampling rate for barometers
uint8_t upwind_oversampling = 0x0;
uint8_t downwind_oversampling = 0x0;
uint8_t ambient_oversampling = 0x0;
uint8_t intake_oversampling = 0x0;

void setup_barometers() {

  TCA.openChannel(TCA_CHANNEL_1);
  barometer_upwind.begin(Wire);
  TCA.closeChannel(TCA_CHANNEL_1);
  
  TCA.openChannel(TCA_CHANNEL_2);
  barometer_downwind.begin(Wire);
  TCA.closeChannel(TCA_CHANNEL_2);
  
  TCA.openChannel(TCA_CHANNEL_3);
  barometer_ambient.begin(Wire);
  TCA.closeChannel(TCA_CHANNEL_3);

  TCA.openChannel(TCA_CHANNEL_7);
  barometer_intake.begin(Wire);
  TCA.closeChannel(TCA_CHANNEL_7);
}

void set_barometer_oversampling(uint8_t * setting, float value) {
  if (value == 1)
    *setting = 0x0;
  else if (value == 2)
    *setting = 0x1;
  else if (value == 4)
    *setting = 0x2;
  else if (value == 8)
    *setting = 0x3;
  else
    fail("er03");
}

float read_barometer_upwind() {
  float pressure;
  TCA.openChannel(TCA_CHANNEL_1);
  barometer_upwind.measurePressureOnce(pressure, upwind_oversampling);
  TCA.closeChannel(TCA_CHANNEL_1);
  return pressure;
}

float read_barometer_downwind() {
  float pressure;
  TCA.openChannel(TCA_CHANNEL_2);
  barometer_downwind.measurePressureOnce(pressure, downwind_oversampling);
  TCA.closeChannel(TCA_CHANNEL_2);
  return pressure;
}

float read_barometer_ambient() {
  float pressure;
  TCA.openChannel(TCA_CHANNEL_3);
  barometer_ambient.measurePressureOnce(pressure, ambient_oversampling);
  TCA.closeChannel(TCA_CHANNEL_3);
  return pressure;
}

float read_barometer_intake() {
  float pressure;
  TCA.openChannel(TCA_CHANNEL_7);
  barometer_intake.measurePressureOnce(pressure, intake_oversampling);
  TCA.closeChannel(TCA_CHANNEL_7);
  return pressure;
}


/*----------------------------*/
/* Potentiometers */

MCP4151 potentiometer_1(PIN_POT_1_CS, MOSI, MISO, SCK);
MCP4151 potentiometer_2(PIN_POT_2_CS, MOSI, MISO, SCK);
byte setting_pot_1;
byte setting_pot_2;

// I keep the additional setting_pot_x variable so that I can output
// no noise if pot_1 is set to zero (see output_noise below)

void set_pot_1_level(float value){
  potentiometer_1.writeValue(value);
  setting_pot_1 = (byte) value;
}

void set_pot_2_level(float value){
  potentiometer_2.writeValue(value);
  setting_pot_2 = (byte) value;
}

/* float read_pot_1_level() { */
/*   float level = pot_1.getCurValue(); */
/*   if (level != (float) setting_pot_1) */
/*     fail("err05"); */
/* } */

/* float read_pot_2_level() { */
/*   float level = pot_2.getCurValue(); */
/*   if (level != (float) setting_pot_2) */
/*     fail("err05"); */
/* } */

/*----------------------------*/
/* Speaker */

uint32_t Rnd; // For the white noise
byte LowBit;  //     generation

void output_noise() {
  if (setting_pot_1) {
    LowBit = Rnd & 1;
    digitalWrite(PIN_NOISE, LowBit); // About 6uS/bit
    Rnd >>= 1;
    Rnd ^= LowBit ? 0x80000057ul : 0ul;
  } else
    digitalWrite(PIN_NOISE, LOW);
}

/*----------------------------*/
/* Analog sensors */

unsigned int signal_1_oversampling = 1;
unsigned int signal_2_oversampling = 1;
unsigned int mic_oversampling = 1;
unsigned int current_in_oversampling = 1;
unsigned int current_out_oversampling = 1;
uint8_t signal_1_reference = DEFAULT;
uint8_t signal_2_reference = DEFAULT;
uint8_t mic_reference = DEFAULT;
uint8_t current_in_reference = DEFAULT;
uint8_t current_out_reference = DEFAULT;

/*----------------------------*/
/* General chamber control */

bool intervention_flag;
float control_target;

/*-----------------------------------------------------------------------*/
/* CHAMBER CONFIGURATIONS */
/*   - variables (names & exogenous or not)
     - setter functions
     - take_measurements(...) function */

#define NA -9999

/* ---------------------------------------------------------------- */
/* Standard configuration */
/*   All manipulable variables are exogenous */

// List of available variables that this board transmits through serial
#define CHAMBER_CONFIG "CHAMBER_CONFIG,standard"
#define VARIABLES_LIST "VARIABLES_LIST,counter,flag,intervention,hatch,pot_1,pot_2,osr_1,osr_2,osr_mic,osr_in,osr_out,osr_upwind,osr_downwind,osr_ambient,osr_intake,v_1,v_2,v_mic,v_in,v_out,load_in,load_out,current_in,current_out,res_in,res_out,rpm_in,rpm_out,pressure_upwind,pressure_downwind,pressure_ambient,pressure_intake,mic,signal_1,signal_2"
#define NO_VARIABLES 35

#define counter 0
#define flag 1
#define intervention 2
#define hatch 3
#define pot_1 4
#define pot_2 5
#define osr_1 6
#define osr_2 7
#define osr_mic 8
#define osr_in 9
#define osr_out 10
#define osr_upwind 11
#define osr_downwind 12
#define osr_ambient 13
#define osr_intake 14
#define v_1 15
#define v_2 16
#define v_mic 17
#define v_in 18
#define v_out 19
#define load_in 20
#define load_out 21
#define current_in 22
#define current_out 23
#define res_in 24
#define res_out 25
#define rpm_in 26
#define rpm_out 27
#define pressure_upwind 28
#define pressure_downwind 29
#define pressure_ambient 30
#define pressure_intake 31
#define mic 32
#define signal_1 33
#define signal_2 34

float variables[NO_VARIABLES];

bool exogenous[NO_VARIABLES] = {
                                false // counter
                                , true // flag
                                , false // intervention
                                , true // hatch
                                , true // pot_1
                                , true // pot_2
                                , true // osr_1
                                , true // osr_2
                                , true // osr_mic
                                , true // osr_in
                                , true // osr_out
                                , true // osr_upwind
                                , true // osr_downwind
                                , true // osr_ambient
                                , true // osr_intake
                                , true // v_1
                                , true // v_2
                                , true // v_mic
                                , true // v_in
                                , true // v_out
                                , true // load_in
                                , true // load_out
                                , false // current_in
                                , false // current_out
                                , true // res_in
                                , true // res_out
                                , false // rpm_in
                                , false // rpm_out
                                , false // pressure_upwind
                                , false // pressure_downwind
                                , false // pressure_ambient
                                , false // pressure_intake
                                , false // mic
                                , false // signal_1
                                , false // signal_2
};

void take_measurements(float * measurements, float obs_counter) {
  // Chamber flags
  measurements[0] = obs_counter;
  measurements[flag] = variables[flag];
  measurements[intervention] = intervention_flag;

  // Exogenous variables
  measurements[hatch] = variables[hatch];
  measurements[pot_1] = variables[pot_1];
  measurements[pot_2] = variables[pot_2];
  measurements[osr_1] = variables[osr_1];
  measurements[osr_2] = variables[osr_2];
  measurements[osr_mic] = variables[osr_mic];
  measurements[osr_in] = variables[osr_in];
  measurements[osr_out] = variables[osr_out];
  measurements[osr_upwind] = variables[osr_upwind];
  measurements[osr_downwind] = variables[osr_downwind];
  measurements[osr_ambient] = variables[osr_ambient];
  measurements[osr_intake] = variables[osr_intake];
  measurements[v_1] = variables[v_1];
  measurements[v_2] = variables[v_2];
  measurements[v_mic] = variables[v_mic];
  measurements[v_in] = variables[v_in];
  measurements[v_out] = variables[v_out];
  measurements[load_in] = variables[load_in];
  measurements[load_out] = variables[load_out];
  measurements[res_in] = variables[res_in];
  measurements[res_out] = variables[res_out];
  
  // Sensor measurements
  measurements[current_in] = analog_avg(PIN_FAN_IN_CURRENT, current_in_oversampling, current_in_reference);
  measurements[current_out] = analog_avg(PIN_FAN_OUT_CURRENT, current_out_oversampling, current_out_reference);
  measurements[rpm_in] = get_rpm_in();
  measurements[rpm_out] = get_rpm_out();
  measurements[pressure_upwind] = read_barometer_upwind();
  measurements[pressure_downwind] = read_barometer_downwind();
  measurements[pressure_ambient] = read_barometer_ambient();
  measurements[pressure_intake] = read_barometer_intake();
  measurements[mic] = analog_avg(PIN_MIC, mic_oversampling, mic_reference);
  measurements[signal_1] = analog_avg(PIN_SGN_POT_1, signal_1_oversampling, signal_1_reference);
  measurements[signal_2] = analog_avg(PIN_SGN_POT_2, signal_2_oversampling, signal_2_reference);

  // Overwrite if sensor is intervened (i.e. variables[target] != NA)
  measurements[current_in] = (variables[current_in] == NA) ? measurements[current_in] : variables[current_in];
  measurements[current_out] = (variables[current_out] == NA) ? measurements[current_out] : variables[current_out];
  measurements[rpm_in] = (variables[rpm_in] == NA) ? measurements[rpm_in] : variables[rpm_in];
  measurements[rpm_out] = (variables[rpm_out] == NA) ? measurements[rpm_out] : variables[rpm_out];
  measurements[pressure_upwind] = (variables[pressure_upwind] == NA) ? measurements[pressure_upwind] : variables[pressure_upwind];
  measurements[pressure_downwind] = (variables[pressure_downwind] == NA) ? measurements[pressure_downwind] : variables[pressure_downwind];
  measurements[pressure_ambient] = (variables[pressure_ambient] == NA) ? measurements[pressure_ambient] : variables[pressure_ambient];
  measurements[pressure_intake] = (variables[pressure_intake] == NA) ? measurements[pressure_intake] : variables[pressure_intake];
  measurements[mic] = (variables[mic] == NA) ? measurements[mic] : variables[mic];
  measurements[signal_1] = (variables[signal_1] == NA) ? measurements[signal_1] : variables[signal_1];
  measurements[signal_2] = (variables[signal_2] == NA) ? measurements[signal_2] : variables[signal_2];
}


/* ---------------------------------------------------------------- */
/* Pressure-control configuration */
/*   PID controller on load_in/load_out to keep pressure_downwind at a given level. */

/* #define CHAMBER_CONFIG "CHAMBER_CONFIG,pressure-control" */
/* #define VARIABLES_LIST "VARIABLES_LIST,counter,flag,intervention,hatch,pot_1,pot_2,osr_1,osr_2,osr_mic,osr_in,osr_out,osr_upwind,osr_downwind,osr_ambient,osr_intake,v_1,v_2,v_mic,v_in,v_out,load_in,load_out,current_in,current_out,res_in,res_out,rpm_in,rpm_out,pressure_upwind,pressure_downwind,pressure_ambient,pressure_intake,mic,signal_1,signal_2,input,error,delta_error,sum_error,gain_p,gain_i,gain_d,output" */

/* #define NO_VARIABLES 43 */

/* #define counter 0 */
/* #define flag 1 */
/* #define intervention 2 */
/* #define hatch 3 */
/* #define pot_1 4 */
/* #define pot_2 5 */
/* #define osr_1 6 */
/* #define osr_2 7 */
/* #define osr_mic 8 */
/* #define osr_in 9 */
/* #define osr_out 10 */
/* #define osr_upwind 11 */
/* #define osr_downwind 12 */
/* #define osr_ambient 13 */
/* #define osr_intake 14 */
/* #define v_1 15 */
/* #define v_2 16 */
/* #define v_mic 17 */
/* #define v_in 18 */
/* #define v_out 19 */
/* #define load_in 20 */
/* #define load_out 21 */
/* #define current_in 22 */
/* #define current_out 23 */
/* #define res_in 24 */
/* #define res_out 25 */
/* #define rpm_in 26 */
/* #define rpm_out 27 */
/* #define pressure_upwind 28 */
/* #define pressure_downwind 29 */
/* #define pressure_ambient 30 */
/* #define pressure_intake 31 */
/* #define mic 32 */
/* #define signal_1 33 */
/* #define signal_2 34 */
/* // Control variables */
/* #define input 35 // Control input, i.e., target pressure */
/* #define error 36 */
/* #define delta_error 37 */
/* #define sum_error 38 */
/* #define gain_p 39 */
/* #define gain_i 40 */
/* #define gain_d 41 */
/* #define output 42 */

/* float variables[NO_VARIABLES]; */

/* bool exogenous[NO_VARIABLES] = { */
/*                                 false // counter */
/*                                 , true // flag */
/*                                 , false // intervention */
/*                                 , true // hatch */
/*                                 , true // pot_1 */
/*                                 , true // pot_2 */
/*                                 , true // osr_1 */
/*                                 , true // osr_2 */
/*                                 , true // osr_mic */
/*                                 , true // osr_in */
/*                                 , true // osr_out */
/*                                 , true // osr_upwind */
/*                                 , true // osr_downwind */
/*                                 , true // osr_ambient */
/*                                 , true // osr_intake */
/*                                 , true // v_1 */
/*                                 , true // v_2 */
/*                                 , true // v_mic */
/*                                 , true // v_in */
/*                                 , true // v_out */
/*                                 , false // load_in */
/*                                 , false // load_out */
/*                                 , false // current_in */
/*                                 , false // current_out */
/*                                 , true // res_in */
/*                                 , true // res_out */
/*                                 , false // rpm_in */
/*                                 , false // rpm_out */
/*                                 , false // pressure_upwind */
/*                                 , false // pressure_downwind */
/*                                 , false // pressure_ambient */
/*                                 , false // pressure_intake */
/*                                 , false // mic */
/*                                 , false // signal_1 */
/*                                 , false // signal_2 */
/*                                 , false // input */
/*                                 , false // error */
/*                                 , false // delta_error */
/*                                 , false // sum_error */
/*                                 , false // gain_p */
/*                                 , false // gain_i */
/*                                 , false // gain_d */
/*                                 , false // output */
/* }; */


/* float previous_error, control_sum_error; */
/* const float control_gain_p = -0.5; */
/* const float control_gain_d = -0.1; */
/* const float control_gain_i = -1e-3; */

/* void take_measurements(float * measurements, float obs_counter) { */
/*   /\* Control loop *\/ */
/*   // NOTE: To avoid affecting measurement times, perform all */
/*   // calculations in control loop even if load_in/load_out are */
/*   // intervened */
/*   // Read chamber pressure (overwrite if pressure_downwind is intervened) */
/*   float pressure = read_barometer_downwind(); */
/*   pressure = (variables[pressure_downwind] == NA) ? pressure : variables[pressure_downwind]; */
/*   measurements[pressure_downwind] = pressure; */
/*   // Compute control output */
/*   float control_error = pressure - control_target; */
/*   float control_delta_error = control_error - previous_error; */
/*   float control_output = control_gain_p * control_error + control_gain_d * control_delta_error + control_gain_i * control_sum_error; */
/*   control_output = max(min(control_output, 1.0), -1.0); */
/*   previous_error = control_error; */
/*   control_sum_error += control_error; */
/*   float control_in, control_out; */
/*   if (control_output > 0) { */
/*     control_in = control_output; */
/*     control_out = 0.01; */
/*   } else { */
/*     control_in = 0.01; */
/*     control_out = -control_output; */
/*   } */
/*   // Set control output (unless load_in / load_out are intervened) */
/*   if (variables[load_in] == NA) { */
/*     set_fan_load(&fan_in, control_in); */
/*     measurements[load_in] = control_in; */
/*   } else { */
/*     measurements[load_in] = variables[load_in]; */
/*   } */
/*   if (variables[load_out] == NA) { */
/*     set_fan_load(&fan_out, control_out); */
/*     measurements[load_out] = control_out; */
/*   } else { */
/*     measurements[load_out] = variables[load_out]; */
/*   } */

/*   /\* Take measurements *\/ */
/*   // Chamber flags */
/*   measurements[0] = obs_counter; */
/*   measurements[flag] = variables[flag]; */
/*   measurements[intervention] = intervention_flag; */

/*   // Exogenous variables */
/*   measurements[hatch] = variables[hatch]; */
/*   measurements[pot_1] = variables[pot_1]; */
/*   measurements[pot_2] = variables[pot_2]; */
/*   measurements[osr_1] = variables[osr_1]; */
/*   measurements[osr_2] = variables[osr_2]; */
/*   measurements[osr_mic] = variables[osr_mic]; */
/*   measurements[osr_in] = variables[osr_in]; */
/*   measurements[osr_out] = variables[osr_out]; */
/*   measurements[osr_upwind] = variables[osr_upwind]; */
/*   measurements[osr_downwind] = variables[osr_downwind]; */
/*   measurements[osr_ambient] = variables[osr_ambient]; */
/*   measurements[osr_intake] = variables[osr_intake]; */
/*   measurements[v_1] = variables[v_1]; */
/*   measurements[v_2] = variables[v_2]; */
/*   measurements[v_mic] = variables[v_mic]; */
/*   measurements[v_in] = variables[v_in]; */
/*   measurements[v_out] = variables[v_out]; */
/*   // measurements[load_in] = variables[load_in]; Set in control loop */
/*   // measurements[load_out] = variables[load_out]; Set in control loop */
/*   measurements[res_in] = variables[res_in]; */
/*   measurements[res_out] = variables[res_out]; */
  
/*   // Sensor measurements */
/*   measurements[current_in] = analog_avg(PIN_FAN_IN_CURRENT, current_in_oversampling, current_in_reference); */
/*   measurements[current_out] = analog_avg(PIN_FAN_OUT_CURRENT, current_out_oversampling, current_out_reference); */
/*   measurements[rpm_in] = get_rpm_in(); */
/*   measurements[rpm_out] = get_rpm_out(); */
/*   measurements[pressure_upwind] = read_barometer_upwind(); */
/*   // measurements[pressure_downwind] = read_barometer_downwind(); Measured in control loop */
/*   measurements[pressure_ambient] = read_barometer_ambient(); */
/*   measurements[pressure_intake] = read_barometer_intake(); */
/*   measurements[mic] = analog_avg(PIN_MIC, mic_oversampling, mic_reference); */
/*   measurements[signal_1] = analog_avg(PIN_SGN_POT_1, signal_1_oversampling, signal_1_reference); */
/*   measurements[signal_2] = analog_avg(PIN_SGN_POT_2, signal_2_oversampling, signal_2_reference); */

/*   // Overwrite if sensor is intervened (i.e. variables[var] != NA) */
/*   measurements[current_in] = (variables[current_in] == NA) ? measurements[current_in] : variables[current_in]; */
/*   measurements[current_out] = (variables[current_out] == NA) ? measurements[current_out] : variables[current_out]; */
/*   measurements[rpm_in] = (variables[rpm_in] == NA) ? measurements[rpm_in] : variables[rpm_in]; */
/*   measurements[rpm_out] = (variables[rpm_out] == NA) ? measurements[rpm_out] : variables[rpm_out]; */
/*   measurements[pressure_upwind] = (variables[pressure_upwind] == NA) ? measurements[pressure_upwind] : variables[pressure_upwind]; */
/*   // measurements[pressure_downwind] = (variables[pressure_downwind] == NA) ? measurements[pressure_downwind] : variables[pressure_downwind]; Measured in control loop */
/*   measurements[pressure_ambient] = (variables[pressure_ambient] == NA) ? measurements[pressure_ambient] : variables[pressure_ambient]; */
/*   measurements[pressure_intake] = (variables[pressure_intake] == NA) ? measurements[pressure_intake] : variables[pressure_intake]; */
/*   measurements[mic] = (variables[mic] == NA) ? measurements[mic] : variables[mic]; */
/*   measurements[signal_1] = (variables[signal_1] == NA) ? measurements[signal_1] : variables[signal_1]; */
/*   measurements[signal_2] = (variables[signal_2] == NA) ? measurements[signal_2] : variables[signal_2]; */

/*   // Control loop diagnosis */
/*   measurements[input] = control_target; */
/*   measurements[error] = control_error; */
/*   measurements[delta_error] = control_delta_error; */
/*   measurements[sum_error] = control_sum_error; */
/*   measurements[gain_p] = control_gain_p; */
/*   measurements[gain_i] = control_gain_i; */
/*   measurements[gain_d] = control_gain_d; */
/*   measurements[output] = control_output; */
/* } */




/*-----------------------------------------------------------------------*/
/* SETTER FUNCTIONS  */

// counter and intervention are always set internally and they don't
// have a setter function

void set_flag(float value) {
  variables[flag] = value;
}

void set_hatch(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[hatch])
      fail("er42");
    else
      variables[hatch] = NA;
  } else {
    variables[hatch] = value;
    // Physical effect
    set_angle(&motor, value);
  }
}

void set_pot_1(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[pot_1])
      fail("er42");
    else
      variables[pot_1] = NA;
  } else if (value >= 0 && value <= 255) {
    variables[pot_1] = value;    
    // Physical effect
    set_pot_1_level(value);
  } else
    fail("er03");
}

void set_pot_2(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[pot_2])
      fail("er42");
    else
      variables[pot_2] = NA;
  } else if (value >= 0 && value <= 255) {
    variables[pot_2] = value;    
    // Physical effect
    set_pot_2_level(value);
  } else
    fail("er03");
}


void set_osr_in(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[osr_in])
      fail("er42");
    else
      variables[osr_in] = NA;
  } else {
    set_oversampling(&current_in_oversampling, value); // Values are checked here
    variables[osr_in] = value;
  } 
}

void set_v_in(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[v_in])
      fail("er42");
    else
      variables[v_in] = NA;
  } else {
    set_reference_voltage(&current_in_reference,value); // Values are checked here
    variables[v_in] = value;
  }
}

void set_osr_out(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[osr_out])
      fail("er42");
    else
      variables[osr_out] = NA;
  } else {
    set_oversampling(&current_out_oversampling, value); // Values are checked here
    variables[osr_out] = value;
  } 
}

void set_v_out(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[v_out])
      fail("er42");
    else
      variables[v_out] = NA;
  } else {
    set_reference_voltage(&current_out_reference,value); // Values are checked here
    variables[v_out] = value;
  }
}

void set_osr_1(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[osr_1])
      fail("er42");
    else
      variables[osr_1] = NA;
  } else {
    set_oversampling(&signal_1_oversampling, value); // Values are checked here
    variables[osr_1] = value;
  } 
}

void set_v_1(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[v_1])
      fail("er42");
    else
      variables[v_1] = NA;
  } else {
    set_reference_voltage(&signal_1_reference,value); // Values are checked here
    variables[v_1] = value;
  }
}

void set_osr_2(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[osr_2])
      fail("er42");
    else
      variables[osr_2] = NA;
  } else {
    set_oversampling(&signal_2_oversampling, value); // Values are checked here
    variables[osr_2] = value;
  } 
}

void set_v_2(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[v_2])
      fail("er42");
    else
      variables[v_2] = NA;
  } else {
    set_reference_voltage(&signal_2_reference,value); // Values are checked here
    variables[v_2] = value;
  }
}

void set_osr_mic(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[osr_mic])
      fail("er42");
    else
      variables[osr_mic] = NA;
  } else {
    set_oversampling(&mic_oversampling, value); // Values are checked here
    variables[osr_mic] = value;
  } 
}

void set_v_mic(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[v_mic])
      fail("er42");
    else
      variables[v_mic] = NA;
  } else {
    set_reference_voltage(&mic_reference,value); // Values are checked here
    variables[v_mic] = value;
  }
}


void set_osr_upwind(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[osr_upwind])
      fail("er42");
    else
      variables[osr_upwind] = NA;
  } else {
    set_barometer_oversampling(&upwind_oversampling, value); // Values are checked here
    variables[osr_upwind] = value;
  }
}

void set_osr_downwind(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[osr_downwind])
      fail("er42");
    else
      variables[osr_downwind] = NA;
  } else {
    set_barometer_oversampling(&downwind_oversampling, value); // Values are checked here
    variables[osr_downwind] = value;
  }
}

void set_osr_ambient(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[osr_ambient])
      fail("er42");
    else
      variables[osr_ambient] = NA;
  } else {
    set_barometer_oversampling(&ambient_oversampling, value); // Values are checked here
    variables[osr_ambient] = value;
  }
}

void set_osr_intake(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[osr_intake])
      fail("er42");
    else
      variables[osr_intake] = NA;
  } else {
    set_barometer_oversampling(&intake_oversampling, value); // Values are checked here
    variables[osr_intake] = value;
  }
}

void set_load_in(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[load_in])
      fail("er42");
    else
      variables[load_in] = NA;
  } else if (value >= 0 && value <= 1) {
    variables[load_in] = value;
    // Physical effect
    set_fan_load(&fan_in, value);
  } else {
    fail("er03");
  }
}

void set_load_out(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[load_out])
      fail("er42");
    else
      variables[load_out] = NA;
  } else if (value >= 0 && value <= 1) {
    variables[load_out] = value;
    // Physical effect
    set_fan_load(&fan_out, value);
  } else {
    fail("er03");
  }
}

void set_res_in(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[res_in])
      fail("er42");
    else
      variables[res_in] = NA;
  } else if (value == 0 || value == 1) {
    fan_in_high_res = (value == 1);
    variables[res_in] = value;
  } else
    fail("er03");
}

void set_res_out(float value) {
  // Check value
  if (value == NA) {
    if (exogenous[res_out])
      fail("er42");
    else
      variables[res_out] = NA;
  } else if (value == 0 || value == 1) {
    fan_out_high_res = (value == 1);
    variables[res_out] = value;
  } else
    fail("er03");
}

// Sensor measurements

void set_current_in(float value) {
  // Check value
  if (value == NA && exogenous[current_in])
    fail("er42");
  else
    variables[current_in] = value;
}

void set_current_out(float value) {
  // Check value
  if (value == NA && exogenous[current_out])
    fail("er42");
  else
    variables[current_out] = value;
}

void set_rpm_in(float value) {
  // Check value
  if (value == NA && exogenous[rpm_in])
    fail("er42");
  else
    variables[rpm_in] = value;
}

void set_rpm_out(float value) {
  // Check value
  if (value == NA && exogenous[rpm_out])
    fail("er42");
  else
    variables[rpm_out] = value;
}

void set_pressure_upwind(float value) {
  // Check value
  if (value == NA && exogenous[pressure_upwind])
    fail("er42");
  else
    variables[pressure_upwind] = value;
}

void set_pressure_downwind(float value) {
  // Check value
  if (value == NA && exogenous[pressure_downwind])
    fail("er42");
  else
    variables[pressure_downwind] = value;
}

void set_pressure_ambient(float value) {
  // Check value
  if (value == NA && exogenous[pressure_ambient])
    fail("er42");
  else
    variables[pressure_ambient] = value;
}

void set_pressure_intake(float value) {
  // Check value
  if (value == NA && exogenous[pressure_intake])
    fail("er42");
  else
    variables[pressure_intake] = value;
}

void set_mic(float value) {
  // Check value
  if (value == NA && exogenous[mic])
    fail("er42");
  else
    variables[mic] = value;
}

void set_signal_1(float value) {
  // Check value
  if (value == NA && exogenous[signal_1])
    fail("er42");
  else
    variables[signal_1] = value;
}

void set_signal_2(float value) {
  // Check value
  if (value == NA && exogenous[signal_2])
    fail("er42");
  else
    variables[signal_2] = value;
}

/* ---------------------------------------------------------------- */
/* Setup function */

void setup() {

  // Set diagnostic leds
  pinMode(PIN_MSR_LED,OUTPUT);
  pinMode(PIN_SET_LED,OUTPUT);
  digitalWrite(PIN_MSR_LED, HIGH);
  digitalWrite(PIN_SET_LED, HIGH);

  // Setup display
  setup_display();
  set_display_color(32,32,32);
  print_top("Initializing");
  print_bottom("  display");   

  // Set variable map
  for (int i; i < NO_VARIABLES; i++)
    variables[i] = NA;
  
  // Setup PWM for fans
  print_bottom("  pwm");
  setup_fans();
  if (exogenous[load_in])
    set_load_in(0.01);
  else
    set_fan_load(&fan_in, 0.01);
  if (exogenous[load_out])
    set_load_out(0.01);
  else
    set_fan_load(&fan_out, 0.01);

  // Attach interrupts to tachometer pins and timer
  print_bottom("  tachometers");
  pinMode(PIN_FAN_IN_TACH, INPUT_PULLUP);
  pinMode(PIN_FAN_OUT_TACH, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_FAN_IN_TACH), tick_fan_in, FALLING);
  attachInterrupt(digitalPinToInterrupt(PIN_FAN_OUT_TACH), tick_fan_out, FALLING);

  // Set up I2C Multiplexer (Hub)
  print_bottom("  multiplexer");
  TCA.begin(Wire);
  
  // Set high precision barometer sensors
  print_bottom("  barometers");
  setup_barometers();

  // Set target to first pressure measurement
  control_target = read_barometer_downwind();
  
  // Set up speaker and amplification circuit
  print_bottom("  speaker");
  // Potentiometers
  pinMode(53, OUTPUT); // Hardware CS pin, must be set to output (https://forum.arduino.cc/t/arduino-mega-2560-pin-53-ss-problem/380656/2)
  set_pot_1(0);
  set_pot_2(0);
  pinMode(PIN_SGN_POT_1, INPUT);
  pinMode(PIN_SGN_POT_2, INPUT);
  // White noise on speaker pin
  pinMode(PIN_NOISE, OUTPUT);
  Entropy.initialize();
  uint32_t Seed = Entropy.random();
  randomSeed(Seed);
  do {
    Rnd = random();
  } while (!Rnd);

  // Attach interrupts (contained in function interrupt)
  Timer1.attachInterrupt(interrupt);
  
  // Setup motor
  print_bottom("  motor");
  setup_motor(motor);

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
float measurements[NO_VARIABLES] = {NA}; // counter + sensor readings

void loop() {
  // Read and decode an instruction from serial
  if (Serial.available() == 0) { // Nothing on the serial line
    take_measurements(measurements,0.0);
  } else {
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
      else if (instruction.target.equals("hatch"))
        set_hatch(value);
      else if (instruction.target.equals("pot_1"))
        set_pot_1(value);
      else if (instruction.target.equals("pot_2"))
        set_pot_2(value);
      else if (instruction.target.equals("osr_1"))
        set_osr_1(value);
      else if (instruction.target.equals("osr_2"))
        set_osr_2(value);
      else if (instruction.target.equals("osr_mic"))
        set_osr_mic(value);
      else if (instruction.target.equals("osr_in"))
        set_osr_in(value);
      else if (instruction.target.equals("osr_out"))
        set_osr_out(value);
      else if (instruction.target.equals("osr_upwind"))
        set_osr_upwind(value);
      else if (instruction.target.equals("osr_downwind"))
        set_osr_downwind(value);
      else if (instruction.target.equals("osr_ambient"))
        set_osr_ambient(value);
      else if (instruction.target.equals("osr_intake"))
        set_osr_intake(value);
      else if (instruction.target.equals("v_1"))
        set_v_1(value);
      else if (instruction.target.equals("v_2"))
        set_v_2(value);
      else if (instruction.target.equals("v_mic"))
        set_v_mic(value);
      else if (instruction.target.equals("v_in"))
        set_v_in(value);
      else if (instruction.target.equals("v_out"))
        set_v_out(value);
      else if (instruction.target.equals("load_in"))
        set_load_in(value);
      else if (instruction.target.equals("load_out"))
        set_load_out(value);
      else if (instruction.target.equals("current_in"))
        set_current_in(value);
      else if (instruction.target.equals("current_out"))
        set_current_out(value);
      else if (instruction.target.equals("res_in"))
        set_res_in(value);
      else if (instruction.target.equals("res_out"))
        set_res_out(value);
      else if (instruction.target.equals("rpm_in"))
        set_rpm_in(value);
      else if (instruction.target.equals("rpm_out"))
        set_rpm_out(value);
      else if (instruction.target.equals("pressure_upwind"))
        set_pressure_upwind(value);
      else if (instruction.target.equals("pressure_downwind"))
        set_pressure_downwind(value);
      else if (instruction.target.equals("pressure_ambient"))
        set_pressure_ambient(value);
      else if (instruction.target.equals("pressure_intake"))
        set_pressure_intake(value);
      else if (instruction.target.equals("mic"))
        set_mic(value);
      else if (instruction.target.equals("signal_1"))
        set_signal_1(value);
      else if (instruction.target.equals("signal_2"))
        set_signal_2(value);
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
      set_angle(&motor, 0);
      detachInterrupt(digitalPinToInterrupt(PIN_FAN_IN_TACH));
      detachInterrupt(digitalPinToInterrupt(PIN_FAN_OUT_TACH));
      Timer1.detachInterrupt();
      send_string(String("OK,RST"));
      resetFunc();
    
      /* UNKNOWN INSTRUCTION */
    } else
      fail("er01",msg);
  }
}

void interrupt() {
  output_noise();
}
