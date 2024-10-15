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
from scipy.stats import truncnorm

import pandas as pd

"""
Generates the experiment protocols for the experiments:

- scm_5_reference
- scm_5_red
- scm_5_green
- scm_5_blue

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


def truncated_normal(lo, hi, loc, scale, size, random_state=42):
    if lo > hi:
        raise ValueError("lo must be below hi.")
    a_transformed, b_transformed = (lo - loc) / scale, (hi - loc) / scale
    rv = truncnorm(a_transformed, b_transformed, loc=loc, scale=scale)
    r = rv.rvs(size=size)
    return r


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
# SCM 4

# Adjacency matrix
A = np.array([[0, 1, 0], [0, 0, 0], [0, 1, 0]])
p = len(A)

# Sample weights for W and D
rng_weights = np.random.default_rng(42)
W = A * rng_weights.uniform(0.5, 1, size=A.shape)
D = np.eye(p) * rng_weights.uniform(0, 1, size=A.shape)

print("W")
print(repr(W.T))
print("D")
print(repr(D))

# Normalize W and D so the marginals are always in [0,1]
norm = np.sum(W + D, axis=0, keepdims=True)
W /= norm
D /= norm

# Sample noise-term variances and observational / interventional means
rng = np.random.default_rng(42)
means = rng.uniform(0.3, 0.4, size=p)
stds = rng.uniform(0.1, 0.15, size=p)
shifts = rng.uniform(0.1, 0.11, size=p)
print("Observational means")
print(repr(means))
print("Mean shifts")
print(repr(shifts))
print("Interventional means")
print(repr(means + shifts))
print("Standard deviations")
print(repr(stds))

# ----------------------------

# Number of observations per intervention
N = int(10e3)

# Intervention targets
targets = [None, ("red", 0), ("green", 1), ("blue", 2)]

# Generate protocol for each intervention
for seed, target in enumerate(targets):
    if target is None:
        protocol_name = "scm_5_reference.txt"
    else:
        target, idx = target
        protocol_name = f"scm_5_{target}.txt"
    filename = f"{OUTPUT_DIR}/{protocol_name}"
    print(f"  {protocol_name}")

    # Sample noise
    noise = []
    for i, (m, v, s) in enumerate(zip(means, stds, shifts)):
        if target is None or i != idx:
            # sample from the observational noise distribution
            noise += [truncated_normal(0, 1, m, v, size=N, random_state=seed + i)]
        elif i == idx:
            # i is the intervention target, sample from shifted noise distribution
            noise += [truncated_normal(0, 1, m + s, v, size=N, random_state=seed + i)]
    # Reshape into a N x p matrix
    noise = np.vstack(noise).T

    # Remove edges into intervention target (set parental coefs. to zero)
    W_int = W.copy()
    if target is not None:
        W_int[:, idx] = 0

    Ztilde = np.linalg.inv(np.eye(p) - W_int.T) @ D @ noise.T

    # Scale to actuator ranges
    S = np.diag([255, 255, 255])
    l = np.array([[0, 0, 0]])
    Z = S @ Ztilde + l.T
    Z = Z.T

    # Check actuators are within bounds
    assert (Z.max(axis=0) <= np.array([255, 255, 255])).all()
    assert (Z.min(axis=0) >= np.array([0, 0, 0])).all()

    df = pd.DataFrame(Z, columns=["red", "green", "blue"])
    df.to_csv(f"/tmp/{protocol_name}")

    # Write to protocol
    with open(filename, "w") as f:
        print("# Setup", file=f)
        # Set all actuators to their zero value
        for e, zero in exogenous_zeros.items():
            print(f"SET,{e},{zero}", file=f)

        # Set actuators and take image
        for red, green, blue in Z:
            print("", file=f)
            print(f"SET,red,{int(red)}", file=f)
            print(f"SET,green,{int(green)}", file=f)
            print(f"SET,blue,{int(blue)}", file=f)
            # Measure
            print("MSR,1,0", file=f)
