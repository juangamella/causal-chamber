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
Generates the experiment protocols for the datasets:

- load_in_seed_*

Change the intake fan load at random intervals, while keeping all other actuators constant.

"""

import utils

# Where the generated .txt protocol files are saved
OUTPUT_DIR = "./protocols"

# Dictionary with the exogenous variables and their zero-levels
exogenous_zeros = {
    "load_out": 0,
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
    "osr_mic": 8,
    "osr_upwind": 8,
    "osr_intake": 8,
    "osr_ambient": 8,
    "osr_downwind": 8,
    "res_in": 1,
    "res_out": 1,
}

for seed in range(10):
    dataset_name = f"load_in_seed_{seed}.txt"
    print(f"  {dataset_name}")
    filename = f"{OUTPUT_DIR}/{dataset_name}"

    # Sample instructions
    instructions = utils.set_and_measure(
        {"load_in": {0.01, 0.1, 0.2, 0.5}},
        n_interventions=10,
        n_msr=(100, 300),
        random_state=seed + 10,
    )

    with open(filename, "w") as f:
        # Setup
        print("# Setup", file=f)
        for var, value in exogenous_zeros.items():
            print(f"SET,{var},{value}", file=f)

        # SET first load and wait 10 seconds
        print(instructions[0], file=f)
        print("WAIT,10000", file=f)

        print("\n# Experiment", file=f)
        for instruction in instructions[1:]:
            print(instruction, file=f)
