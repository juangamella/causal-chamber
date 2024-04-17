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

- ir_sensors

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
    "diode_vis_1": 1,
    "diode_vis_2": 1,
    "diode_vis_3": 1,
    "t_vis_1": 3,
    "t_vis_2": 3,
    "t_vis_3": 3,
    "osr_angle_1": 8,
    "osr_angle_2": 8,
    "osr_c": 8,
    "v_c": 1.1,
    "v_angle_1": 5,
    "v_angle_2": 5,
    "green": 0,
    "blue": 0,
}

N = 500
protocol_name = "ir_sensors.txt"
print(f"  {protocol_name}")
filename = f"{OUTPUT_DIR}/{protocol_name}"
rng = np.random.default_rng(42)
with open(filename, "w") as f:
    # Set other exogenous variables
    for e, zero in exogenous_zeros.items():
        print(f"SET,{e},{zero}", file=f)

    # Keep diode fixed, cycle through diodes
    diode = 2
    exposures = [0, 1, 2, 3]
    print("SET,flag,0", file=f)
    print(f"SET,diode_ir_1,{diode}", file=f)
    print(f"SET,diode_ir_2,{diode}", file=f)
    print(f"SET,diode_ir_3,{diode}", file=f)
    for exposure in exposures:
        print(f"SET,t_ir_1,{exposure}", file=f)
        print(f"SET,t_ir_2,{exposure}", file=f)
        print(f"SET,t_ir_3,{exposure}", file=f)
        for i in range(N):
            r = rng.choice(np.arange(256))
            print(f"SET,red,{r}", file=f)
            print("MSR,1,0", file=f)

    # Keep exposure fixed, cycle through diodes
    exposure = 3
    diodes = [0, 1, 2]
    print("SET,flag,1", file=f)
    print(f"SET,t_ir_1,{exposure}", file=f)
    print(f"SET,t_ir_2,{exposure}", file=f)
    print(f"SET,t_ir_3,{exposure}", file=f)
    for diode in diodes:
        print(f"SET,diode_ir_1,{diode}", file=f)
        print(f"SET,diode_ir_2,{diode}", file=f)
        print(f"SET,diode_ir_3,{diode}", file=f)
        for i in range(N):
            r = rng.choice(np.arange(256))
            print(f"SET,red,{r}", file=f)
            print("MSR,1,0", file=f)
