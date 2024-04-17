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

- actuators_white

Sample each actuator $(R,G,B,\theta_1,\theta_2)$ uniformly at random from its full range of values, and take a measurement, while keeping all sensor parameters constant. Repeat $N=32000$ times.

"""

import numpy as np

# Where the generated .txt protocol files are saved
OUTPUT_DIR = "./protocols"

# Generation parameters
N = 30000

sensor_parameters = {
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
    "v_c": 1.1,
}

# Dictionary with the exogenous variables and their zero-levels
ranges = {
    "red": (0, 255),
    "green": (0, 255),
    "blue": (0, 255),
    "pol_1": (-90, 90),
    "pol_2": (-90, 90),
    "l_11": (0, 255),
    "l_12": (0, 255),
    "l_21": (0, 255),
    "l_22": (0, 255),
    "l_31": (0, 255),
    "l_32": (0, 255),
}

# 98145719283
rng = np.random.default_rng(98145719284)


protocol_name = "actuators_white.txt"
print(f"  {protocol_name}")
filename = f"{OUTPUT_DIR}/{protocol_name}"
with open(filename, "w") as f:
    # Set all actuators to their zero value
    for s, v in sensor_parameters.items():
        print(f"SET,{s},{v}", file=f)
    for i in range(N):
        # Set light source levels
        print("", file=f)
        values = dict(
            (v, rng.integers(r[0], r[1], endpoint=True)) for v, r in ranges.items()
        )

        for var, val in values.items():
            print(f"SET,{var},{val}", file=f)
        # Take a measurement
        print("MSR,1,0", file=f)
