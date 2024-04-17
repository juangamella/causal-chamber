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

- random_loads_both

"""

import numpy as np

# Where the generated .txt protocol files are saved
OUTPUT_DIR = "./protocols"

# Dictionary with the exogenous variables and their zero-levels
exogenous_zeros = {
    "hatch": 0,
    "pot_1": 0,
    "pot_2": 0,
    "v_1": 5,
    "osr_1": 1,
    "v_2": 5,
    "osr_2": 1,
    "v_in": 1.1,
    "osr_in": 8,
    "v_out": 1.1,
    "osr_out": 8,
    "v_mic": 5,
    "osr_mic": 1,
    "osr_upwind": 8,
    "osr_intake": 8,
    "osr_ambient": 8,
    "osr_downwind": 8,
    "res_in": 1,
    "res_out": 1,
}


# Generation parameters
T = 100
N = 2000

rng = np.random.default_rng(42)
protocol_name = "random_loads_both.txt"
print(f"  {protocol_name}")
filename = f"{OUTPUT_DIR}/{protocol_name}"

with open(filename, "w") as f:
    # Set other exogenous variables
    for e, zero in exogenous_zeros.items():
        print(f"SET,{e},{zero}", file=f)
    for i in range(N):
        print(f"\nSET,flag,{i}", file=f)
        # Set loads
        load = rng.uniform(0, 1)
        print(f"SET,load_in,{load:.2f}", file=f)
        print(f"SET,load_out,{load:.2f}", file=f)
        # Wait for system to stabilize
        print("WAIT,8000", file=f)
        # Take measurements
        print(f"MSR,{T},0", file=f)
        print("", file=f)
