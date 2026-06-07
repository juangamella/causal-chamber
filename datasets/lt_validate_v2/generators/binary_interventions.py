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
Submits the experiment protocols for the dataset lt_validate_v2.

For each row in lt_validation_configs.csv, all other manipulable variables
are fixed to their context values and the target variable is repeatedly set
to one of two values (xA or xB), chosen uniformly at random, to implement
the binary-intervention validation procedure described in the manuscript.

Submitted experiment IDs are printed to stdout.
"""

import numpy as np
import pandas as pd
import os
import causalchamber.lab as lab

CHAMBER_ID = "lt-demo-ch4lu"
CONFIG = "lt_mk2_standard"
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "/tmp/.credentials")

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, "../lt_validation_configs.csv")
configs = pd.read_csv(filename, header=0)

rng = np.random.default_rng(56192837)

rlab = lab.Lab(credentials_file=CREDENTIALS_FILE)

manipulable_variables = list(configs["target"])

for _, row in configs.iterrows():
    target = row["target"]
    values = [row["xA"], row["xB"]]
    T = int(row["T"])
    N = int(row["N"])

    print(f"  Submitting validate_{target} ...")

    experiment = rlab.new_experiment(CHAMBER_ID, CONFIG)

    # Set all context variables (all manipulable variables except the target)
    for var in manipulable_variables:
        if var != target and not pd.isna(row[var]):
            experiment.set(var, row[var])

    # Collect measurements: random wait, set flag+target, then measure
    waiting_times = rng.integers(1, 1000, endpoint=True, size=N)
    for i in range(N):
        treatment = int(rng.integers(0, 2))
        experiment.wait(int(waiting_times[i]))
        experiment.set("flag", treatment)
        experiment.set(target, values[treatment])
        if T > 0:
            experiment.wait(T)
        experiment.measure(1)

    experiment_id = experiment.submit(tag=f"validate_{target}")
    print(f"    experiment_id: {experiment_id}")

print("Done.")
