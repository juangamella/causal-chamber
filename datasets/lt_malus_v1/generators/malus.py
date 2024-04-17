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
Generates the experiment protocols for the experiments:

- white_64
- white_128
- white_255
- red_64
- red_128
- red_255
- green_64
- green_128
- green_255
- blue_64
- blue_128
- blue_255

"""

import numpy as np

# Where the generated .txt protocol files are saved
OUTPUT_DIR = "./protocols"

# Generation parameters
N = 1000

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
    "osr_c": 8,
    "osr_angle_1": 8,
    "osr_angle_2": 8,
    "v_c": 1.1,
    "v_angle_1": 5,
    "v_angle_2": 5,
    "red": 0,
    "green": 0,
    "blue": 0,
}

rng = np.random.default_rng(42)
pol_range = np.arange(-90, 90, 0.1)

for color in ["white", "red", "green", "blue"]:
    for brightness in [64, 128, 255]:
        protocol_name = f"{color}_{brightness}.txt"
        print(f"  {protocol_name}")
        filename = f"{OUTPUT_DIR}/{protocol_name}"
        with open(filename, "w") as f:
            # Set all other actuators
            for e, zero in exogenous_zeros.items():
                if e != color:
                    print(f"SET,{e},{zero}", file=f)
            # Set light source color and brightness
            if color in ["red", "white"]:
                print(f"SET,red,{brightness}", file=f)
            if color in ["green", "white"]:
                print(f"SET,green,{brightness}", file=f)
            if color in ["blue", "white"]:
                print(f"SET,blue,{brightness}", file=f)
            # Move polarizers to random angles and take measurements
            for i in range(N):
                # Set target at random
                print("", file=f)
                print("SET,pol_1,%0.1f" % rng.choice(pol_range), file=f)
                print("SET,pol_2,%0.1f" % rng.choice(pol_range), file=f)
                # Measure
                print("MSR,1,0", file=f)
