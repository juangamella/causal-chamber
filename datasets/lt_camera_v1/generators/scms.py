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

"""
Generates the experiment protocols for the experiments:

- scm_1_reference
- scm_1_red
- scm_1_green
- scm_1_blue
- scm_1_pol_1
- scm_1_pol_2

"""


def to_float(param):
    """Transform a camera parameter (e.g. ISO, f-stop (aperture) or
    shutter speed) from string into a float.

    Examples
    --------
    >>> to_float("1/200")
    0.005
    >>> to_float('3"')
    180.0
    >>> to_float('1.8')
    1.8
    >>> to_float('22')
    22.0
    """
    if param[-1] == '"':
        return float(eval(param[:-1]) * 60)
    else:
        return float(eval(param))


# Where the generated .txt protocol files are saved
OUTPUT_DIR = "./protocols"

# Dictionary with the exogenous variables and their zero-levels
exogenous_zeros = {
    "red": 0,
    "green": 0,
    "blue": 0,
    "l_11": 0,
    "l_12": 0,
    "l_21": 0,
    "l_22": 0,
    "l_31": 0,
    "l_32": 0,
    "pol_1": 0,
    "pol_2": 0,
    "diode_ir_1": 2,
    "diode_ir_2": 2,
    "diode_ir_3": 2,
    "diode_vis_1": 1,
    "diode_vis_2": 1,
    "diode_vis_3": 1,
    "t_ir_1": 3,
    "t_ir_2": 3,
    "t_ir_3": 3,
    "t_vis_1": 3,
    "t_vis_2": 3,
    "t_vis_3": 3,
    "osr_c": 1,
    "osr_angle_1": 1,
    "osr_angle_2": 1,
    "v_c": 5,
    "v_angle_1": 5,
    "v_angle_2": 5,
    "camera": 1,
    "aperture": "1.8",
    "iso": "500",
    "shutter_speed": "1/200",
}


# ----------------------------
# SCM 1
# Adjacency matrix
A = np.array(
    [
        [0, 1, 0, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0],
    ]
)
p = len(A)

# Sample weights for W and D
rng_weights = np.random.default_rng(42)
W = A * rng_weights.uniform(0.5, 1, size=A.shape)
D = np.eye(p) * rng_weights.uniform(0, 1, size=A.shape)

# Normalize W and D so the marginals are always in [0,1]
norm = np.sum(W + D, axis=0, keepdims=True)
W /= norm
D /= norm
# ----------------------------

# Number of observations per intervention
N = int(5e3)

# Intervention targets
targets = [None, ("red", 0), ("green", 1), ("blue", 2), ("pol_1", 3), ("pol_2", 4)]

# Generate protocol for each intervention
for seed, target in enumerate(targets):
    if target is None:
        protocol_name = "scm_1_reference.txt"
    else:
        target, idx = target
        protocol_name = f"scm_1_{target}.txt"
    filename = f"{OUTPUT_DIR}/{protocol_name}"
    print(f"  {protocol_name}")

    # Sample distribution
    rng = np.random.default_rng(seed)
    noise = rng.uniform(0, 1, size=(N, p))

    # Perform intervention
    W_int = W.copy()
    if target is not None:
        # Perform intervention (shift noise term, remove parents)
        noise[:, idx] = rng.uniform(0.75, 1, size=N)
        W_int[:, idx] = 0

    Ztilde = np.linalg.inv(np.eye(p) - W_int.T) @ D @ noise.T

    # Scale to actuator ranges
    S = np.diag([255, 255, 255, 180, 180])
    l = np.array([[0, 0, 0, -90, -90]])
    Z = S @ Ztilde + l.T
    Z = Z.T

    # Check actuators are within bounds
    assert (Z.max(axis=0) <= np.array([255, 255, 255, 90, 90])).all()
    assert (Z.min(axis=0) >= np.array([0, 0, 0, -90, -90])).all()

    # Write to protocol
    with open(filename, "w") as f:
        print("# Setup", file=f)
        # Set all actuators to their zero value
        for e, zero in exogenous_zeros.items():
            print(f"SET,{e},{zero}", file=f)

        # Set actuators and take image
        for red, green, blue, pol_1, pol_2 in Z:
            print("", file=f)
            print(f"SET,red,{int(red)}", file=f)
            print(f"SET,green,{int(green)}", file=f)
            print(f"SET,blue,{int(blue)}", file=f)
            print(f"SET,pol_1,{pol_1:0.1f}", file=f)
            print(f"SET,pol_2,{pol_2:0.1f}", file=f)
            # Measure
            print("MSR,1,0", file=f)
