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


"""Generates the experiment protocols for the experiments:

- loads_hatch_mix_<fast,slow>: sets the loads and hatch to a sine,
  square and step signal, respectively

"""

import numpy as np

# Where the generated .txt protocol files are saved
OUTPUT_DIR = "./protocols"

# Generation parameters
N = 10000

# Dictionary with the exogenous variables and their zero-levels
exogenous_zeros = {
    "pot_1": 0,
    "pot_2": 0,
    "osr_1": 1,
    "osr_2": 1,
    "osr_in": 8,
    "osr_out": 8,
    "osr_mic": 1,
    "osr_upwind": 8,
    "osr_downwind": 8,
    "osr_intake": 8,
    "osr_ambient": 8,
    "v_1": 5,
    "v_2": 5,
    "v_in": 1.1,
    "v_out": 1.1,
    "v_mic": 5,
    "res_in": 1,
    "res_out": 1,
}


for speed in ["fast", "slow"]:
    # Taken from https://scikit-learn.org/stable/auto_examples/decomposition/plot_ica_blind_source_separation.html
    T = 8 if speed == "slow" else 32
    time = np.linspace(0.1, T, N)
    np.sin(time / T * np.pi / 2)
    load_in = (np.sin(2 * time) + 1) / 2  # Signal 1 : sinusoidal signal
    load_in = np.maximum(load_in, 0.01)
    load_out = (np.sign(np.sin(3 * time)) + 1) / 2  # Signal 2 : square signal
    load_out = np.maximum(load_out, 0.01)
    hatch = np.sign(np.sin(time / 8 * np.pi * 2))
    hatch[hatch == 0] = 1
    hatch = (1 - hatch) / 2 * 45

    protocol_name = f"loads_hatch_mix_{speed}.txt"
    print(f"  {protocol_name}")
    filename = f"{OUTPUT_DIR}/{protocol_name}"
    with open(filename, "w") as f:
        # Set all actuators to their zero value
        for e, zero in exogenous_zeros.items():
            print(f"SET,{e},{zero}", file=f)
        print("WAIT,5000", file=f)
        for lin, lout, h in zip(load_in, load_out, hatch):
            # Set light source levels
            print("", file=f)
            print(f"SET,load_in,{lin:.4f}", file=f)
            print(f"SET,load_out,{lout:.4f}", file=f)
            print(f"SET,hatch,{h:.2f}", file=f)
            # Take a measurement
            print("MSR,1,0", file=f)
