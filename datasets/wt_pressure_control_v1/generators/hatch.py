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

- hatch_0

The hatch and all other exogenous, manipulable variables of the system (i.e. all actuators and sensor parameters except $L_\text{in}, L_\text{out}$) are kept at a constant value, and measurements are taken at full frequency. The experiment is repeated from different hatch positions.

"""

# Where the generated .txt protocol files are saved
OUTPUT_DIR = "./protocols"

# Dictionary with the exogenous variables and their zero-levels
exogenous_zeros = {
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
    "osr_mic": 8,
    "osr_upwind": 8,
    "osr_intake": 8,
    "osr_ambient": 8,
    "osr_downwind": 8,
    "res_in": 1,
    "res_out": 1,
}

N = 10000
for hatch in [0]:
    protocol_name = f"hatch_{hatch}.txt"
    print(f"  {protocol_name}")
    filename = f"{OUTPUT_DIR}/{protocol_name}"
    with open(filename, "w") as f:
        # Set hatch and other exogenous variables
        print(f"SET,hatch,{hatch}", file=f)
        for e, zero in exogenous_zeros.items():
            print(f"SET,{e},{zero}", file=f)
        # Set initial conditions
        print("WAIT,7000", file=f)
        # Perform the experiment
        print(f"MSR,{N},0\n", file=f)
