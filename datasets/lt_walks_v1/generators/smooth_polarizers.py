# MIT License

# Copyright (c) 2023 Juan L. Gamella

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

- smooth_polarizers

"""

import numpy as np
import pandas as pd

# Where the generated .txt protocol files are saved
OUTPUT_DIR = "./protocols"

# Generation parameters
N = 10000

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
    "pol_2": 0,
}

rng = np.random.default_rng(981457149301)

# Generate actuator sequences


# Red: uniformly at random, two blocks
# Blue: uniformly at random,

inputs = rng.uniform(128 - 64, 128 + 64, size=(N, 5))
scales = np.array(
    [
        [0.5, 1, 1.2, 1.328125, 1.3],
        [1.328125, 0.7, 1.1, 1.2, 1],
        [1, 0.4, 1.3, 1, 1.328],
    ]
)

# Define blocks (3 blocks)
b1 = int(N / 2)
b2 = int(N / 3)
b3 = N - b1 - b2

blocks = np.array([0] * b1 + [1] * b2 + [2] * b3)

for i in range(3):
    inputs[blocks == i] *= scales[i]

actuators = pd.DataFrame(
    {
        "flag": blocks,
        "pol_1": np.linspace(-90, 180, N),
        "red": inputs[:, 0],
        "green": inputs[:, 1],
        "blue": inputs[:, 2],
        "l_31": inputs[:, 3],
        "l_32": inputs[:, 4],
    }
)

# actuators.to_csv("/tmp/smooth_polarizers.csv")

protocol_name = "smooth_polarizers.txt"
print(f"  {protocol_name}")
filename = f"{OUTPUT_DIR}/{protocol_name}"
with open(filename, "w") as f:
    # Set all actuators to their zero value
    for s, v in sensor_parameters.items():
        print(f"SET,{s},{v}", file=f)

    for i in range(N):
        # Set actuators
        print("", file=f)
        print(f"SET,flag,{int(actuators.iloc[i].flag)}", file=f)
        print(f"SET,pol_1,{actuators.iloc[i].pol_1:0.1f}", file=f)
        print(f"SET,red,{int(actuators.iloc[i].red)}", file=f)
        print(f"SET,green,{int(actuators.iloc[i].green)}", file=f)
        print(f"SET,blue,{int(actuators.iloc[i].blue)}", file=f)
        print(f"SET,l_31,{int(actuators.iloc[i].l_31)}", file=f)
        print(f"SET,l_32,{int(actuators.iloc[i].l_32)}", file=f)

        # Measure
        print("MSR,1,0", file=f)
