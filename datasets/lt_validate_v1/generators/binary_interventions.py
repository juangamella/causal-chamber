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

import numpy as np
import pandas as pd
import os

"""
Generates the experiment protocols for the datasets:

- random_<var_name>: fixes all other manipulable variables to a given
value (see lt_manipulable_configs.csv), and samples <var> uniformly at
random according to min/max columns in lt_manipulable_configs.csv.
"""

# Import manipulable configs (also used for wt_validate dataset)
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, "../lt_validation_configs.csv")
configs = pd.read_csv(filename, header=0)
OUTPUT_DIR = "./protocols"

rng = np.random.default_rng(56192837)

# Generate protocols
for counter, row in configs.iterrows():
    target = row.target
    values = [row["xA"], row["xB"]]
    T = row["T"]
    N = row["N"]
    # Write experiment protocol
    DATASET_NAME = f"validate_{target}.txt"
    print(f"  {DATASET_NAME}")
    filename = f"{OUTPUT_DIR}/{DATASET_NAME}"
    with open(filename, "w") as f:
        print("# Setup", file=f)
        # Do not use the camera (separate dataset lt_validate_camera)
        print("SET,camera,0", file=f)
        # Set all other manipulable variables to the desired value
        manipulable_variables = configs.target  # List of manipulable variables
        for var in manipulable_variables:
            if var != target:
                print(f"SET,{var},{row[var]}", file=f)
        # Begin procedure
        #   sample waiting times between 1 and 1000 milliseconds
        waiting_times = rng.integers(1, 1000, endpoint=True, size=N)
        print("\n# Collect measurements", file=f)
        for i in range(N):
            treatment = rng.choice([0, 1])
            print(f"WAIT,{waiting_times[i]}", file=f)
            print(f"SET,flag,{treatment}", file=f)
            print(f"SET,{target},{values[treatment]}", file=f)
            if T > 0:
                print(f"WAIT,{T}", file=f)
            print("MSR,1,0", file=f)

print(f"Generated {counter+1} protocols")
