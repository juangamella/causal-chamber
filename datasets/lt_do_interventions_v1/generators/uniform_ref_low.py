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

- uniform_ref_low: All manipulable variables uniformly at random from the bottom half of their full range. Categorical actuators are sampled from the first two values (except diode_vis_*, which always takes value=1)

"""

import numpy as np

# Where the generated .txt protocol files are saved
OUTPUT_DIR = "./protocols"

# Generation parameters
N = int(1e5)  # 100K

# Dictionary with the exogenous variables and their zero-levels
variable_ranges = {
    "red": (0, 128),
    "green": (0, 128),
    "blue": (0, 128),
    "osr_c": [1, 2],
    "v_c": [5, 2.56],
    "pol_1": (-180, 0),
    "pol_2": (-180, 0),
    "osr_angle_1": [1, 2],
    "osr_angle_2": [1, 2],
    "v_angle_1": [5, 2.56],
    "v_angle_2": [5, 2.56],
    "l_11": (0, 128),
    "l_12": (0, 128),
    "l_21": (0, 128),
    "l_22": (0, 128),
    "l_31": (0, 128),
    "l_32": (0, 128),
    "diode_ir_1": [2, 1],
    "diode_ir_2": [2, 1],
    "diode_ir_3": [2, 1],
    "diode_vis_1": [1],
    "diode_vis_2": [1],
    "diode_vis_3": [1],
    "t_ir_1": [3, 2],
    "t_ir_2": [3, 2],
    "t_ir_3": [3, 2],
    "t_vis_1": [3, 2],
    "t_vis_2": [3, 2],
    "t_vis_3": [3, 2],
}


rng = np.random.default_rng(1726235328)


def sample_value(variable):
    interval = variable_ranges[variable]
    if type(interval) == list:
        values = interval
    elif type(interval) == tuple:
        lo, hi = interval
        if variable in ["pol_1", "pol_2"]:
            values = np.arange(lo, hi + 0.1, 0.1)
        else:
            values = np.arange(lo, hi + 1)
    # Sample
    return rng.choice(values)


flag = 0
protocol_name = "uniform_ref_low.txt"
print(f"  {protocol_name}")
filename = f"{OUTPUT_DIR}/{protocol_name}"
# Generate the protocol
with open(filename, "w") as f:
    print(f"SET,flag,{flag}", file=f)
    print("SET,camera,0\n\n", file=f)

    for i in range(N):
        # Sample and set actuator values
        for variable in variable_ranges.keys():
            value = sample_value(variable)
            fmt = "%0.2f" % value if type(value) == np.float64 else "%d" % value
            print(f"SET,{variable},{fmt}", file=f)
        # Take a measurement
        print("MSR,1,0\n", file=f)
