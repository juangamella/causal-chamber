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
import sempler
import pandas as pd

"""
Generates the experiment protocols for the experiments:

- buchholz_1_obs
- buchholz_1_red
- buchholz_1_green
- buchholz_1_blue
- buchholz_1_pol_1
- buchholz_1_pol_2

"""

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


# Number of observations per intervention
N = int(1e4)

# ----------------------------
# Define SCM

rng = np.random.default_rng(471917254012300182764)

# First, define the SCM from which to sample. For the noise variances
# we sample from the same interval as the in the paper

d = 5  # nr. of latent dims

W = np.array(
    [
        [0.0, 0.0, 0.0, 0.0, 0.0],
        [0.71943922, 0.0, 0.0, 0.0, 0.67726298],
        [0.0, 0.89303215, 0.0, 0.0, 0.98534901],
        [0.84868401, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0],
    ]
)

variances_obs = rng.uniform(1.0, 2.0, size=d)

lganm = sempler.LGANM(
    W=W, means=np.zeros(d), variances=variances_obs, random_state=4719820817
)

# Next, get the samples from the observational distribution. We store
# their mean and std_dev for later scaling

obs_sample = lganm.sample(N)
means = np.mean(obs_sample, axis=0, keepdims=True)
stds = np.std(obs_sample, axis=0, keepdims=True)

print("# Obs. means\nobs_means =", repr(np.zeros(d)))
print("# Obs. variances\nobs_vars =", repr(variances_obs))

obs_sample = (obs_sample - means) / stds

# Now, sample from the interventional distributions. The mean and
# variances of the do-interventions are again sampled from the same
# intervals as in the original paper. We also apply the sign random
# sign flipping to the interventional means as the authors do.

means_iv = rng.uniform(1.0, 2.0, size=d)
mask = rng.binomial(n=1, p=0.5, size=means_iv.size).reshape(means_iv.shape)
means_iv = means_iv - 2 * mask * means_iv
variances_iv = rng.uniform(1.0, 2.0, size=d)

print("# Intervention means\nint_means =", repr(means_iv))
print("# Intervention variances\nint_vars =", repr(variances_iv))

iv_samples = []
for i in range(d):
    sample = lganm.sample(N, do_interventions={i: (means_iv[i], variances_iv[i])})
    sample = (sample - means) / stds  # Rescale using params of observational data
    iv_samples.append(sample)

# The latents are now clipped to an interval of C std devs around 0 in
# order to enable their rescaling to the correct intervals for the
# chamber actuators.
C = 5
obs_sample = np.clip(obs_sample, a_min=-C, a_max=C)
iv_samples = [np.clip(sample, a_min=-C, a_max=C) for sample in iv_samples]

# Apply rescaling to match actuator ranges (that expects 4 std_devs
# around 0 of clipping interval)
scales_up = np.array([[255 / (2 * C), 255 / (2 * C), 255 / (2 * C), 90 / C, 90 / C]])
shifts_up = np.array([[127.5, 127.5, 127.5, 0, 0]])

actuators = [obs_sample] + iv_samples
actuators = [sample * scales_up + shifts_up for sample in actuators]

# Check actuators are within bounds
for sample in actuators:
    assert (sample.max(axis=0) <= np.array([255, 255, 255, 90, 90])).all()
    assert (sample.min(axis=0) >= np.array([0, 0, 0, -90, -90])).all()

# ----------------------------


# Intervention targets
targets = [None, ("red", 0), ("green", 1), ("blue", 2), ("pol_1", 3), ("pol_2", 4)]

# Generate protocol for each intervention
for seed, target in enumerate(targets):
    if target is None:
        protocol_name = "buchholz_1_obs.txt"
    else:
        target, idx = target
        protocol_name = f"buchholz_1_{target}.txt"
    filename = f"{OUTPUT_DIR}/{protocol_name}"
    print(f"  {protocol_name}")

    Z = actuators[0 if target is None else idx + 1]

    df = pd.DataFrame(Z, columns=["red", "green", "blue", "pol_1", "pol_2"])
    df.to_csv(f"/tmp/{protocol_name}")

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
