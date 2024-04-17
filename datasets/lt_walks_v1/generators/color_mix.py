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

- color_mix: vary the red,green,blue values according to a sine, square and sawtooth wave, respectively

"""

import numpy as np

# import matplotlib.pyplot as plt
from scipy import signal

# Where the generated .txt protocol files are saved
OUTPUT_DIR = "./protocols"

# Generation parameters
N = 10000

# Dictionary with the exogenous variables and their zero-levels
exogenous_zeros = {
    "l_11": 0,
    "l_12": 0,
    "l_21": 0,
    "l_22": 0,
    "l_31": 0,
    "l_32": 0,
    "pol_1": 90,
    "pol_2": 0,
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
    "osr_angle_1": 1,
    "osr_angle_2": 1,
    "v_c": 5,
    "v_angle_1": 5,
    "v_angle_2": 5,
}


for noise in [0]:  # , 0.01]:
    # Taken from https://scikit-learn.org/stable/auto_examples/decomposition/plot_ica_blind_source_separation.html
    time = np.linspace(0.1, 8, N)
    red = np.sin(2 * time)  # Signal 1 : sinusoidal signal
    green = np.sign(np.sin(3 * time))  # Signal 2 : square signal
    blue = signal.sawtooth(2 * np.pi * time)  # Signal 3: saw tooth signal

    # Add noise
    colors = np.c_[red, green, blue]
    colors += noise * np.random.normal(size=colors.shape)

    # Quantize
    colors -= colors.min(axis=0)
    colors /= colors.max(axis=0)
    colors *= 255
    colors = colors.astype(int)

    protocol_name = f"color_mix{'_noise' if noise != 0 else ''}.txt"
    print(f"  {protocol_name}")
    filename = f"{OUTPUT_DIR}/{protocol_name}"
    with open(filename, "w") as f:
        # Set all actuators to their zero value
        for e, zero in exogenous_zeros.items():
            print(f"SET,{e},{zero}", file=f)
        for color in colors:
            # Set light source levels
            print("", file=f)
            print(f"SET,red,{color[0]}", file=f)
            print(f"SET,green,{color[1]}", file=f)
            print(f"SET,blue,{color[2]}", file=f)
            # Take a measurement
            print("MSR,1,0", file=f)
