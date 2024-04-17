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

- load_out_1_osr_downwind_4
- load_out_0.5_osr_downwind_4
- load_out_0.5_osr_downwind_2
- load_out_0.01_osr_downwind_4
- load_out_0.5_osr_downwind_8

load_out is kept at a fixed load and hatch is sampled uniformly at random from [0,45].
"""

import numpy as np

# Where the generated .txt protocol files are saved
OUTPUT_DIR = "./protocols"

# Dictionary with the exogenous variables and their zero-levels
exogenous_zeros = {
    "pot_1": 0,
    "pot_2": 0,
    "osr_1": 1,
    "osr_2": 1,
    "osr_in": 8,
    "osr_out": 2,
    "osr_upwind": 4,
    "osr_intake": 4,
    "osr_ambient": 4,
    "v_1": 5,
    "v_2": 5,
    "v_in": 1.1,
    "v_out": 1.1,
    "v_mic": 5,
    "res_in": 1,
    "res_out": 1,
}

# Generation parameters
N = 5000

rng = np.random.default_rng(7)

settings = [
    # Training (and Pup)
    {"load_out": 0.5, "osr_downwind": 4},
    # load_out = 1
    {"load_out": 1, "osr_downwind": 4},
    # load_out = 0.01
    {"load_out": 0.01, "osr_downwind": 4},
    # osr: 2
    {"load_out": 0.5, "osr_downwind": 2},
    # osr: 8
    {"load_out": 0.5, "osr_downwind": 8},
]


for setting in settings:
    load_out = setting["load_out"]
    osr = setting["osr_downwind"]
    dataset_name = f"load_out_{load_out}_osr_downwind_{osr}.txt"
    print(f"  {dataset_name}")
    filename = f"{OUTPUT_DIR}/{dataset_name}"
    with open(filename, "w") as f:
        # Set other exogenous variables
        for e, zero in exogenous_zeros.items():
            print(f"SET,{e},{zero}", file=f)
        # Set shifts
        print(f"SET,load_out,{load_out:.2f}", file=f)  # Set exhaust load
        print(f"SET,osr_downwind,{osr}", file=f)  # Set barometer precision
        print("WAIT,7000\n", file=f)  # Wait for system to stabilize
        for i in range(N):
            hatch = rng.uniform(0, 45)
            # --------------------------
            print("# Impulse curve no. %d" % (i + 1), file=f)
            print(f"SET,flag,{i}", file=f)
            # --------------------------
            print(f"SET,hatch,{hatch:.1f}", file=f)  # Set hatch
            print("SET,load_in,0.01", file=f)  # Intake to 1%
            # --------------------------
            print("WAIT,500", file=f)  # Wait for system to stabilize
            print("# Impulse", file=f)
            print("MSR,5,0", file=f)  # Measure initial conditions
            print("SET,load_in,1", file=f)  # Impulse
            print("MSR,20,0", file=f)
            print("SET,load_in,0.01", file=f)
            print("MSR,25,0", file=f)
            print("", file=f)
