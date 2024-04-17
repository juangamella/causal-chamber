# MIT License

# Copyright (c) 2024 Juan L. Gamella

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""
Generates the experiment protocols for the experiment:

- angle_sensors

"""

import numpy as np

# Where the generated .txt protocol files are saved
OUTPUT_DIR = "./protocols"

# Dictionary with the exogenous variables and their zero-levels
exogenous_zeros = {
    "l_11": 0,
    "l_12": 0,
    "l_21": 0,
    "l_22": 0,
    "l_31": 0,
    "l_32": 0,
    "diode_ir_1": 2,
    "diode_ir_2": 2,
    "diode_ir_3": 2,
    "diode_vis_1": 1,
    "diode_vis_2": 1,
    "diode_vis_3": 1,
    "t_ir_1": 3,
    "t_ir_2": 3,
    "t_ir_3": 3,
    "t_vis_1": 3,
    "t_vis_2": 3,
    "t_vis_3": 3,
    "osr_c": 1,
    "v_c": 5,
    "red": 128,
    "green": 128,
    "blue": 128,
}

protocol_name = "angle_sensors.txt"
print(f"  {protocol_name}")
filename = f"{OUTPUT_DIR}/{protocol_name}"
with open(filename, "w") as f:
    # Set other exogenous variables
    for e, zero in exogenous_zeros.items():
        print(f"SET,{e},{zero}", file=f)

    # Test increments of polarizer angles
    print("SET,flag,0", file=f)
    print("SET,v_angle_1,5", file=f)
    print("SET,v_angle_2,5", file=f)
    for osr in [1, 2, 4, 8]:
        print(f"SET,osr_angle_1,{osr}", file=f)
        print(f"SET,osr_angle_2,{osr}", file=f)
        print("MSR,512,0", file=f)

    # Test increments of polarizer angles
    print("SET,flag,1", file=f)
    print("SET,osr_angle_1,1", file=f)
    print("SET,osr_angle_2,1", file=f)
    for vref in [1.1, 2.56, 5]:
        print(f"SET,v_angle_1,{vref}", file=f)
        print(f"SET,v_angle_2,{vref}", file=f)
        for angle in np.arange(-180, 180, 1):
            print(f"SET,pol_1,{angle:.2f}", file=f)
            print(f"SET,pol_2,{angle:.2f}", file=f)
            print("MSR,1,0", file=f)
