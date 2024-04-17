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

- potis_coarse
- potis_fine



"""

import numpy as np

# Where the generated .txt protocol files are saved
OUTPUT_DIR = "./protocols"

# Dictionary with the exogenous variables and their zero-levels
exogenous_zeros = {
    "load_in": 0,
    "load_out": 0,
    "hatch": 0,
    "v_in": 1.1,
    "v_out": 1.1,
    "v_1": 5,
    "v_2": 5,
    "v_mic": 5,
    "osr_mic": 8,
    "osr_1": 1,
    "osr_2": 1,
    "osr_in": 8,
    "osr_out": 8,
    "osr_upwind": 8,
    "osr_intake": 8,
    "osr_ambient": 8,
    "osr_downwind": 8,
    "res_in": 1,
    "res_out": 1,
}


rng = np.random.default_rng(15987918267)

for level in ["fine", "coarse"]:
    protocol_name = f"potis_{level}.txt"
    print(f"  {protocol_name}")
    filename = f"{OUTPUT_DIR}/{protocol_name}"
    with open(filename, "w") as f:
        # Set other exogenous variables
        for e, zero in exogenous_zeros.items():
            print(f"SET,{e},{zero}", file=f)

        print("WAIT,7000", file=f)

        if level == "fine":
            for a1 in range(256):
                print(f"\nSET,pot_1,{a1}", file=f)
                for a2 in range(256):
                    print(f"SET,pot_2,{a2}", file=f)
                    print("MSR,1,0", file=f)

        elif level == "coarse":
            for a1 in np.linspace(0, 255, 10, dtype=int):
                print(f"\nSET,pot_1,{a1}", file=f)
                for a2 in np.linspace(0, 255, 10, dtype=int):
                    print(f"SET,pot_2,{a2}", file=f)
                    print("MSR,10,0", file=f)
