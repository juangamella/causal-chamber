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

- actuators_random_walk

Standard configuration of the wind tunnel. Actuators variables follow
independent random walks; sensor parameters are fixed (see values
below in dictionary `sensor_parameters`).

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
    "hatch": (0, 45, 0.1),
    "pot_1": (0, 255, 1),
    "pot_2": (0, 255, 1),
}

for seed in np.arange(1, 16 + 1):
    protocol_name = f"actuators_random_walk_{seed}.txt"
    print(f"  {protocol_name}")
    filename = f"{OUTPUT_DIR}/{protocol_name}"

    rng = np.random.default_rng(seed)

    # Sample max step sizes
    walk_params = {}
    print("    max step sizes:") if plot else None
    for actuator, (lo, hi, res) in actuator_params.items():
        max_step_size = rng.uniform(res, (hi - lo) / 50)
        print(f"      {actuator} : {max_step_size}") if plot else None
        walk_params[actuator] = (lo, hi, max_step_size, res)

    # Generate walks
    walks = {}
    for j, (actuator, (lo, hi, step, res)) in enumerate(walk_params.items()):
        walks[actuator] = rw(
            N, lo, hi, step, res, random_state=rng.integers(0, 2**32 - 1)
        )
        if plot:
            plt.subplot(len(walk_params), 1, j + 1)
            plt.plot(walks[actuator])
            plt.ylabel(actuator, rotation=0)
    plt.show() if plot else None

    # Write protocol
    with open(filename, "w") as f:
        # Set all actuators to their zero value
        for sensor, param in sensor_parameters.items():
            print(f"SET,{sensor},{param}\n", file=f)
        for i in range(N):
            for actuator, walk in walks.items():
                print(f"SET,{actuator},{walk[i]:.2f}", file=f)
            # Take a measurement
            print("MSR,1,0", file=f)
