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

- actuators_white_single

"""

import numpy as np
from scipy.stats import truncnorm
import pandas as pd
import causalchamber.ground_truth as gt


# ----------------------------------------------------------------------
# White noise from a truncated gaussian
def truncated_normal(lo, hi, loc, scale, size, random_state=42):
    if lo > hi:
        raise ValueError("lo must be below hi.")
    a_transformed, b_transformed = (lo - loc) / scale, (hi - loc) / scale
    rv = truncnorm(a_transformed, b_transformed, loc=loc, scale=scale)
    r = rv.rvs(size=size)
    return r


plot = False
if plot:
    import matplotlib.pyplot as plt

# Where the generated .txt protocol files are saved
OUTPUT_DIR = "./protocols"

# Generation parameters
N = 1000

# Dictionary with the parameters for the random walk:
#   - min, max possible values
#   - max step size
#   - resolution (e.g., 1 for ints)

sensor_parameters = {
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

actuator_params = {  # min /max
    "load_in": (0, 1),
    "load_out": (0, 1),
    "pot_1": (0, 255),
    "pot_2": (0, 255),
}

intervention_targets = {
    "hatch": [0, 45],
    "res_in": [1, 0],
    "res_out": [1, 0],
    "osr_upwind": [8, 1],
    "osr_downwind": [8, 1],
    "osr_ambient": [8, 1],
    "osr_intake": [8, 1],
    "v_in": [1.1, 5],
    "v_out": [1.1, 5],
    "v_1": [5, 2.56],
    "v_2": [5, 2.56],
}

rng = np.random.default_rng(13)

DELAY = 500

protocol_name = "actuators_white_single.txt"
print(f"  {protocol_name}")
filename = f"{OUTPUT_DIR}/{protocol_name}"

print("TARGETS")
targets = [None] + list(actuator_params.keys()) + list(intervention_targets.keys())
print(repr(targets))

latex = [r"\emptyset"] + [gt.latex_name(v, enclose=False) for v in targets[1:]]
string = ""
for l in latex:
    string += l + ", "
print(string)

# Write protocol
seed = 0
with open(filename, "w") as f:
    # Set all actuators to their reference value
    for sensor, param in sensor_parameters.items():
        print(f"SET,{sensor},{param}", file=f)

    # -------------------------
    # Observational environment

    # Sample white-noise for actuators given by actuator_params.keys()
    flag = 0
    signals = {}
    mean, std = 0.3, 0.07
    for actuator, (lo, hi) in actuator_params.items():
        # Sample from truncated normal
        Z = truncated_normal(0, 1, mean, std, size=N, random_state=seed)
        seed += 1
        # Scale
        signals[actuator] = Z * (hi - lo) + lo
        assert signals[actuator].max() <= hi and signals[actuator].min() >= lo
        # For verification
        pd.DataFrame(signals).to_csv(f"/tmp/actuators_white_flag_{flag}.csv")

    # Write experiment protocol
    print(f"\n\nSET,flag,{flag}", file=f)
    # Set intervention targets to their observational value
    for t, (v0, v1) in intervention_targets.items():
        print(f"SET,{t},{v0}", file=f)
    # Collect data
    for i in range(N):
        # Set actuators
        print("", file=f)
        for actuator, signal in signals.items():
            if actuator in ["load_in", "load_out"]:
                print(f"SET,{actuator},{signal[i]:.2f}", file=f)
            else:
                print(f"SET,{actuator},{int(signal[i])}", file=f)
        # Take measurement
        print(f"MSR,1,{DELAY}", file=f)

    # -------------------------
    # Shifted actuators

    for j, target in enumerate(actuator_params.keys()):
        flag = 1 + j
        print(flag)
        # Sample white noise for actuators
        signals = {}
        int_mean, int_std = 0.5, 0.15
        for actuator, (lo, hi) in actuator_params.items():
            # Sample from truncated normal
            if actuator == target:
                Z = truncated_normal(0, 1, int_mean, int_std, size=N, random_state=seed)
            else:
                Z = truncated_normal(0, 1, mean, std, size=N, random_state=seed)
            seed += 1
            # Scale
            signals[actuator] = Z * (hi - lo) + lo
            assert signals[actuator].max() <= hi and signals[actuator].min() >= lo
            # For verification
            pd.DataFrame(signals).to_csv(f"/tmp/actuators_white_flag_{flag}.csv")

        # Write experiment protocol
        print(f"\n\nSET,flag,{flag}", file=f)
        # Set intervention targets to their observational value
        for t, (v0, v1) in intervention_targets.items():
            print(f"SET,{t},{v0}", file=f)
        # Collect data
        for i in range(N):
            # Set actuators
            print("", file=f)
            for actuator, signal in signals.items():
                if actuator in ["load_in", "load_out"]:
                    print(f"SET,{actuator},{signal[i]:.2f}", file=f)
                else:
                    print(f"SET,{actuator},{int(signal[i])}", file=f)
            # Take measurement
            print(f"MSR,1,{DELAY}", file=f)

    # -------------------------
    # Binary interventions on hatch and sensor parameters

    for j, target in enumerate(intervention_targets.keys()):
        flag = len(actuator_params) + 1 + j
        print(flag)
        # Sample white noise actuators
        signals = {}
        for actuator, (lo, hi) in actuator_params.items():
            # Sample from truncated normal
            Z = truncated_normal(0, 1, mean, std, size=N, random_state=seed)
            seed += 1
            # Scale
            signals[actuator] = Z * (hi - lo) + lo
            assert signals[actuator].max() <= hi and signals[actuator].min() >= lo
            # For verification
            pd.DataFrame(signals).to_csv(f"/tmp/actuators_white_flag_{flag}.csv")

        # Write experiment protocol
        print(f"\n\nSET,flag,{flag}", file=f)
        # Perform intervention on target and set the others to the observational level
        for t, (v0, v1) in intervention_targets.items():
            if t == target:
                print(f"SET,{t},{v1}", file=f)
            else:
                print(f"SET,{t},{v0}", file=f)
        # Collect data
        for i in range(N):
            # Set actuators
            print("", file=f)
            for actuator, signal in signals.items():
                if actuator in ["load_in", "load_out"]:
                    print(f"SET,{actuator},{signal[i]:.2f}", file=f)
                else:
                    print(f"SET,{actuator},{int(signal[i])}", file=f)
            # Take measurement
            print(f"MSR,1,{DELAY}", file=f)
