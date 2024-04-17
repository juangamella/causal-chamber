# Arduino API for MCP4151 digital potentiometer

---

## How to use

Create an instance of it, like `MCP4151 pot(CS, MOSI, MISO, SCK)`.  
Where CS is chip select pin, MOSI is the output on the Arduino, MISO is the input, and SCK is the clock.  
On the MCP4151, the MISO and MOSI are on the same pin. Use a 1 kOhm resistor to pull down the MISO pin  
on the chip to GND, with the MOSI line (on the MOSI pin of the Arduino) in series with the resistor.
There's another constructor that accepts more parameters if one needs more customization.  

Import it into your project with `#include <MCP4151.h>`.  

---

## Available functions

`pot.writeValue()` and `pot.getCurValue()` where 'pot' is the name of the object initialized.  
Function `pot.getCurValue()` retrieves the stored wiper value from the chip. If this isn't needed,  
then connecting the resistor and MISO line are not needed and the Arduino can just have its MOSI line  
connected to the chip's pin 3.

### Will this work with other MCP41x1 chips? Yes probably. Only tested with MCP4151.