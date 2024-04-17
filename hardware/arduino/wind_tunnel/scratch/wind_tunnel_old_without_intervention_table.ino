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
/* Libraries */
#include <Arduino.h>
#include <Wire.h> // For I2C communication

#include "utils.h"
#include "serial_comms.h"

#include <MCP4151.h> // For digital potentiometers
#include <TimerOne.h> // For PWM modulation of LEDs
#include "Dps310.h" // High-precision barometer
#include <TCA9548A.h> // For I2C Multiplexer/Hub
#include <Entropy.h> // for white noise generation using clock jitter

/* Global variables & macros */
#define NA -9999

// List of available variables that this board transmits through serial

#define CHAMBER_CONFIG "CHAMBER_CONFIG,standard"
#define VARIABLES_LIST "VARIABLES_LIST,counter,flag,intervention,hatch,pot_1,pot_2,osr_1,osr_2,osr_mic,osr_in,osr_out,osr_upwind,osr_downwind,osr_ambient,osr_intake,v_1,v_2,v_mic,v_in,v_out,load_in,load_out,current_in,current_out,res_in,res_out,rpm_in,rpm_out,pressure_upwind,pressure_downwind,pressure_ambient,pressure_intake,mic,signal_1,signal_2"
#define NO_VARIABLES 35

/* #define CHAMBER_CONFIG "CHAMBER_CONFIG,pressure_control" */
/* #define VARIABLES_LIST "VARIABLES_LIST,counter,flag,intervention,hatch,pot_1,pot_2,osr_1,osr_2,osr_mic,osr_in,osr_out,osr_upwind,osr_downwind,osr_ambient,osr_intake,v_1,v_2,v_mic,v_in,v_out,load_in,load_out,current_in,current_out,res_in,res_out,rpm_in,rpm_out,pressure_upwind,pressure_downwind,pressure_ambient,pressure_intake,mic,signal_1,signal_2,target,error,delta_error,sum_error,gain_p,gain_i,gain_d" */
/* #define NO_VARIABLES 42 */

/* ------------------------------------------------------------------- */
/* Initializations */

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

struct Fan {
  int pin_pwm;
  int pin_interrupt;
  float load;
  volatile int counter;
};

Fan fan_in = {.pin_pwm = PIN_FAN_IN_PWM, .pin_interrupt = PIN_FAN_IN_TACH, .load = 0, .counter = 0};
Fan fan_out = {.pin_pwm = PIN_FAN_OUT_PWM, .pin_interrupt = PIN_FAN_OUT_TACH, .load = 0, .counter = 0};

Dps310 barometer_upwind = Dps310();
Dps310 barometer_downwind = Dps310();
Dps310 barometer_ambient = Dps310();
Dps310 barometer_intake = Dps310();
TCA9548A<TwoWire> TCA; // I2C Multiplexer/Hub
volatile float flag, rpm_in, rpm_out;
bool intervention_flag;
float target; // The target for any control mechanisms
MCP4151 pot_1(PIN_POT_1_CS, MOSI, MISO, SCK);
MCP4151 pot_2(PIN_POT_2_CS, MOSI, MISO, SCK);
byte setting_pot_1;
byte setting_pot_2;
uint32_t Rnd; // For the white noise
byte LowBit;  //     generation

// Resolution for fan RPM (true = microseconds timer / false = milliseconds timer)
bool fan_in_high_res = true;
bool fan_out_high_res = true;

// Oversampling rate for barometers
uint8_t osr_upwind = 0x0;
uint8_t osr_downwind = 0x0;
uint8_t osr_ambient = 0x0;
uint8_t osr_intake = 0x0;

// Oversampling rate for analog sensors
unsigned int signal_1_oversampling = 1;
unsigned int signal_2_oversampling = 1;
unsigned int mic_oversampling = 1;
unsigned int current_in_oversampling = 1;
unsigned int current_out_oversampling = 1;
// Reference voltage for analog sensors
uint8_t signal_1_reference = DEFAULT;
uint8_t signal_2_reference = DEFAULT;
uint8_t mic_reference = DEFAULT;
uint8_t current_in_reference = DEFAULT;
uint8_t current_out_reference = DEFAULT;

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
    
  // Setup PWM for fans
  print_bottom("  pwm");
  setup_fans();
  set_fan_load(&fan_in, 0.05);
  set_fan_load(&fan_out, 0.05);

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
  target = read_barometer_downwind();
  
  // Set up speaker and amplification circuit
  print_bottom("  speaker");
  // Potentiometers
  pinMode(53, OUTPUT); // Hardware CS pin, must be set to output (https://forum.arduino.cc/t/arduino-mega-2560-pin-53-ss-problem/380656/2)
  set_pot_1_level(0);
  set_pot_2_level(0);
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
float variables[NO_VARIABLES] = {NA}; // counter + sensor readings

void loop() {
  // Read and decode an instruction from serial
  if (Serial.available() == 0) { // Nothing on the serial line
    take_measurements(variables,0.0);
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
      else if (instruction.target.equals("hatch"))
        set_angle(&motor, value);
      else if (instruction.target.equals("pot_1"))
        (value >= 0 && value <= 255) ? set_pot_1_level(value) : fail("er03");
      else if (instruction.target.equals("pot_2"))
        (value >= 0 && value <= 255) ? set_pot_2_level(value) : fail("er03");
      // Oversampling rates
      else if (instruction.target.equals("osr_1"))
        set_oversampling(&signal_1_oversampling, value);
      else if (instruction.target.equals("osr_2"))
        set_oversampling(&signal_2_oversampling, value);
      else if (instruction.target.equals("osr_mic"))
        set_oversampling(&mic_oversampling, value);
      else if (instruction.target.equals("osr_in"))
        set_oversampling(&current_in_oversampling, value);
      else if (instruction.target.equals("osr_out"))
        set_oversampling(&current_out_oversampling, value);
      else if (instruction.target.equals("osr_upwind"))
        set_barometer_oversampling(&osr_upwind, value);
      else if (instruction.target.equals("osr_downwind"))
        set_barometer_oversampling(&osr_downwind, value);
      else if (instruction.target.equals("osr_ambient"))
        set_barometer_oversampling(&osr_ambient, value);
      else if (instruction.target.equals("osr_intake"))
        set_barometer_oversampling(&osr_intake, value);
      // Reference voltages
      else if (instruction.target.equals("v_1"))
        set_reference_voltage(&signal_1_reference,value);
      else if (instruction.target.equals("v_2"))
        set_reference_voltage(&signal_2_reference,value);
      else if (instruction.target.equals("v_mic"))
        set_reference_voltage(&mic_reference,value);
      else if (instruction.target.equals("v_in"))
        set_reference_voltage(&current_in_reference,value);
      else if (instruction.target.equals("v_out"))
        set_reference_voltage(&current_out_reference,value);
      // Fan RPM resolution
      else if (instruction.target.equals("res_in")) {
        if (value == 1)
          fan_in_high_res = true;
        else if (value == 0)
          fan_in_high_res = false;
        else
          fail("er03");
      } else if (instruction.target.equals("res_out")) {
        if (value == 1)
          fan_out_high_res = true;
        else if (value == 0)
          fan_out_high_res = false;
        else
          fail("er03");
      }
      // Fan loads
      else if (instruction.target.equals("load_in"))
        (value >= 0 && value <= 1) ? set_fan_load(&fan_in, value) : fail("er03");
      else if (instruction.target.equals("load_out"))
        (value >= 0 && value <= 1) ? set_fan_load(&fan_out, value) : fail("er03");
      // Target: for control mechanisms
      else if (instruction.target.equals("target"))
        target = value;
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
  //compute_rpm();
}

/*-----------------------------------------------------------------------*/
/* Stepper motor */

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

/*-----------------------------------------------------------------------*/
/* Speaker */

void output_noise() {
  if (setting_pot_1) {
    LowBit = Rnd & 1;
    digitalWrite(PIN_NOISE, LowBit); // About 6uS/bit
    Rnd >>= 1;
    Rnd ^= LowBit ? 0x80000057ul : 0ul;
  } else
    digitalWrite(PIN_NOISE, LOW);
}

/*-----------------------------------------------------------------------*/
/* Barometers */

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
  barometer_upwind.measurePressureOnce(pressure, osr_upwind);
  TCA.closeChannel(TCA_CHANNEL_1);
  return pressure;
}

float read_barometer_downwind() {
  float pressure;
  TCA.openChannel(TCA_CHANNEL_2);
  barometer_downwind.measurePressureOnce(pressure, osr_downwind);
  TCA.closeChannel(TCA_CHANNEL_2);
  return pressure;
}

float read_barometer_ambient() {
  float pressure;
  TCA.openChannel(TCA_CHANNEL_3);
  barometer_ambient.measurePressureOnce(pressure, osr_ambient);
  TCA.closeChannel(TCA_CHANNEL_3);
  return pressure;
}

float read_barometer_intake() {
  float pressure;
  TCA.openChannel(TCA_CHANNEL_7);
  barometer_intake.measurePressureOnce(pressure, osr_intake);
  TCA.closeChannel(TCA_CHANNEL_7);
  return pressure;
}

/*-----------------------------------------------------------------------*/
/* Potentiometers */

void set_pot_1_level(float value){
  pot_1.writeValue(value);
  setting_pot_1 = (byte) value;
}

float read_pot_1_level() {
  float level = pot_1.getCurValue();
  if (level != (float) setting_pot_1)
    fail("err05");
}

void set_pot_2_level(float value){
  pot_2.writeValue(value);
  setting_pot_2 = (byte) value;
}

float read_pot_2_level() {
  float level = pot_2.getCurValue();
  if (level != (float) setting_pot_2)
    fail("err05");
}

/*-----------------------------------------------------------------------*/
/* Fans */

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

void setup_fans() {
  Timer1.initialize(40);
  Timer1.pwm(fan_in.pin_pwm, 0, 40);
  Timer1.pwm(fan_out.pin_pwm, 0, 40);
}

void set_fan_load(Fan *fan, float load) {
  Timer1.setPwmDuty((*fan).pin_pwm, round(1023*load));
  (*fan).load = load;
}

/* ---------------------------------------------------------------- */
/* CHAMBER CONFIGURATIONS */

/* Standard configuration */
/*   All manipulable variables are exogenous */
void take_measurements(float * variables, float counter) {
  variables[0] = counter;
  variables[1] = flag;
  variables[2] = intervention_flag;
  variables[3] = read_angle(motor);
  variables[4] = setting_pot_1; //read_pot_1_level();
  variables[5] = setting_pot_2; //read_pot_2_level();
  variables[6] = signal_1_oversampling;
  variables[7] = signal_2_oversampling;
  variables[8] = mic_oversampling;
  variables[9] = current_in_oversampling;
  variables[10] = current_out_oversampling;
  variables[11] = (float) (1 << osr_upwind);
  variables[12] = (float) (1 << osr_downwind);
  variables[13] = (float) (1 << osr_ambient);
  variables[14] = (float) (1 << osr_intake);
  variables[15] = get_reference_voltage(&signal_1_reference);
  variables[16] = get_reference_voltage(&signal_2_reference);
  variables[17] = get_reference_voltage(&mic_reference);
  variables[18] = get_reference_voltage(&current_in_reference);
  variables[19] = get_reference_voltage(&current_out_reference);
  variables[20] = fan_in.load;
  variables[21] = fan_out.load;
  variables[22] = analog_avg(PIN_FAN_IN_CURRENT, current_in_oversampling, current_in_reference);
  variables[23] = analog_avg(PIN_FAN_OUT_CURRENT, current_out_oversampling, current_out_reference);
  variables[24] = fan_in_high_res;
  variables[25] = fan_out_high_res;
  variables[26] = get_rpm_in();
  variables[27] = get_rpm_out();
  variables[28] = read_barometer_upwind();
  variables[29] = read_barometer_downwind();
  variables[30] = read_barometer_ambient();
  variables[31] = read_barometer_intake();
  variables[32] = analog_avg(PIN_MIC, mic_oversampling, mic_reference);
  variables[33] = analog_avg(PIN_SGN_POT_1, signal_1_oversampling, signal_1_reference);
  variables[34] = analog_avg(PIN_SGN_POT_2, signal_2_oversampling, signal_2_reference);
}

/* /\* Pressure-control configuration *\/ */
/* /\*   PID controller on load_in/load_out to keep pressure_chamber at a given level.  *\/ */

/* float previous_error, sum_error; */
/* const float gain_p = -0.5; */
/* const float gain_d = 0.0; */
/* const float gain_i = -1e-2; */

/* void take_measurements(float * variables, float counter) { */
/*   /\* Control loop *\/ */
/*   // Read chamber pressure */
/*   float pressure = read_barometer_downwind(); */
/*   // Compute control output */
/*   float error = pressure - target; */
/*   float delta_error = error - previous_error; */
/*   float control_output = gain_p * error + gain_d * delta_error + gain_i * sum_error; */
/*   control_output = max(min(control_output, 1.0), -1.0); */
/*   previous_error = error; */
/*   sum_error += error; */
/*   float load_in, load_out; */
/*   if (control_output > 0) { */
/*     load_in = control_output; */
/*     load_out = 0.0; */
/*   } else { */
/*     load_in = 0.0; */
/*     load_out = -control_output; */
/*   } */
/*   // Set control output */
/*   set_fan_load(&fan_in, load_in); */
/*   set_fan_load(&fan_out, load_out); */
/*   /\* Measure other variables *\/ */
/*   variables[0] = counter; */
/*   variables[1] = flag; */
/*   variables[2] = intervention_flag; */
/*   variables[3] = read_angle(motor); */
/*   variables[4] = setting_pot_1; //read_pot_1_level(); */
/*   variables[5] = setting_pot_2; //read_pot_2_level(); */
/*   variables[6] = signal_1_oversampling; */
/*   variables[7] = signal_2_oversampling; */
/*   variables[8] = mic_oversampling; */
/*   variables[9] = current_in_oversampling; */
/*   variables[10] = current_out_oversampling; */
/*   variables[11] = (float) (1 << osr_upwind); */
/*   variables[12] = (float) (1 << osr_downwind); */
/*   variables[13] = (float) (1 << osr_ambient); */
/*   variables[14] = (float) (1 << osr_intake); */
/*   variables[15] = get_reference_voltage(&signal_1_reference); */
/*   variables[16] = get_reference_voltage(&signal_2_reference); */
/*   variables[17] = get_reference_voltage(&mic_reference); */
/*   variables[18] = get_reference_voltage(&current_in_reference); */
/*   variables[19] = get_reference_voltage(&current_out_reference); */
/*   variables[20] = fan_in.load; */
/*   variables[21] = fan_out.load; */
/*   variables[22] = analog_avg(PIN_FAN_IN_CURRENT, current_in_oversampling, current_in_reference); */
/*   variables[23] = analog_avg(PIN_FAN_OUT_CURRENT, current_out_oversampling, current_out_reference); */
/*   variables[24] = fan_in_high_res; */
/*   variables[25] = fan_out_high_res; */
/*   variables[26] = get_rpm_in(); */
/*   variables[27] = get_rpm_out(); */
/*   variables[28] = read_barometer_upwind(); */
/*   variables[29] = pressure; */
/*   variables[30] = read_barometer_ambient(); */
/*   variables[31] = read_barometer_intake(); */
/*   variables[32] = analog_avg(PIN_MIC, mic_oversampling, mic_reference); */
/*   variables[33] = analog_avg(PIN_SGN_POT_1, signal_1_oversampling, signal_1_reference); */
/*   variables[34] = analog_avg(PIN_SGN_POT_2, signal_2_oversampling, signal_2_reference); */
/*   variables[35] = target; */
/*   variables[36] = error; */
/*   variables[37] = delta_error; */
/*   variables[38] = sum_error; */
/*   variables[39] = gain_p; */
/*   variables[40] = gain_i; */
/*   variables[41] = gain_d; */
/* } */
