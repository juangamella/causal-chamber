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

- regime_jumps_single
- regime_jumps_multi

"""

import numpy as np
from sampling import random_walk_mirrored as rw

# ----------------------------------------------------------------------
# Random walk

plot = False
if plot:
    import matplotlib.pyplot as plt

# Where the generated .txt protocol files are saved
OUTPUT_DIR = "./protocols"

# Generation parameters
N_REGIMES = 32
N = 10000

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

actuator_params = {  # min, max, resolution
    "load_in": (0, 1, 0.01),
    "load_out": (0, 1, 0.01),
    "pot_1": (0, 255, 1),
    "pot_2": (0, 255, 1),
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

MAX_TARGETS = 5

for max_targets in [1, MAX_TARGETS]:
    protocol_name = (
        "regime_jumps_single.txt" if max_targets == 1 else "regime_jumps_multi.txt"
    )
    print(f"  {protocol_name}")
    filename = f"{OUTPUT_DIR}/{protocol_name}"

    rng = np.random.default_rng(13)

    # Generate random walks for actuators
    walks = {}
    for j, (actuator, (lo, hi, res)) in enumerate(actuator_params.items()):
        walks[actuator] = rw(
            N * N_REGIMES,
            lo,
            hi,
            res * 5,
            res,
            random_state=rng.integers(0, 2**32 - 1),
        )
        if plot:
            plt.plot(walks[actuator])
            plt.ylabel(actuator, rotation=0)
    plt.show() if plot else None

    # Generate sequence of intervention targets
    regime_targets = [[]]
    for i in range(N_REGIMES - 1):
        # Sample number of targets
        if max_targets == 1:
            n_targets = rng.choice([0, 1], 1, p=[0.3, 0.7])
        else:
            n_targets = rng.integers(0, max_targets, endpoint=True)
        # Sample target variables
        targets = rng.choice(
            list(intervention_targets.keys()), size=n_targets, replace=False
        )
        regime_targets.append(list(targets))
        print(list(targets))

    print(regime_targets)

    # Write protocol
    with open(filename, "w") as f:
        # Set all actuators to their reference value
        for sensor, param in sensor_parameters.items():
            print(f"SET,{sensor},{param}", file=f)

        # Iterate through regimes
        for i in range(N_REGIMES):
            print(f"\n\nSET,flag,{i}", file=f)
            # Perform regime interventions
            for t, (v0, v1) in intervention_targets.items():
                if t in regime_targets[i]:
                    print(f"SET,{t},{v1}", file=f)
                else:
                    print(f"SET,{t},{v0}", file=f)
            # Run actuator walks and take measurements
            print("", file=f)
            for j in range(i * N, (i + 1) * N):
                for actuator, walk in walks.items():
                    print(f"SET,{actuator},{walk[j]:.2f}", file=f)
                # Take a measurement
                print("MSR,1,0", file=f)
