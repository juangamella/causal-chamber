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
from scipy.stats import betabinom

"""
Generates the experiment protocols for the experiments:

- betab_ap_1.8_iso_500.0_ss_0.005'

"""


def betabinomial(lo, hi, alpha, beta, size, random_state=42):
    """Sample `size` observations from a [beta-binomial
    distribution](https://en.wikipedia.org/wiki/Beta-binomial_distribution),
    where the number of trials (n) is given by `hi-lo` and the
    observations `X` are shifted as `lo+X`.
    """
    if lo > hi:
        raise ValueError("lo must be below hi.")
    n = hi - lo
    X = betabinom.rvs(n=n, a=alpha, b=beta, size=size, random_state=random_state)
    return lo + X


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
}

# Generation parameters
N = int(1e4)

# Settings (aperture, iso, shutter_speed)
settings = [
    ("1.8", "500", "1/200"),  # reference
    # ("1.8", "1000", "1/200"),  # higher ISO
    # ("1.8", "500", "1/1000"),  # faster shutter
    # ("8.0", "500", "1/200"),  # smaller aperture
]

count = 0
for seed, (aperture, iso, shutter_speed) in enumerate(settings):
    protocol_name = f"betab_ap_{to_float(aperture)}_iso_{to_float(iso)}_ss_{to_float(shutter_speed)}.txt"
    filename = f"{OUTPUT_DIR}/{protocol_name}"
    print(f"  {protocol_name}")
    with open(filename, "w") as f:
        print("# Setup", file=f)
        # Set all actuators to their zero value
        for e, zero in exogenous_zeros.items():
            print(f"SET,{e},{zero}", file=f)
        # Set iso, aperture and shutter speed
        print("\n# Camera parameters", file=f)
        print("SET,camera,1", file=f)
        print(f"SET,aperture,{aperture}", file=f)
        print(f"SET,iso,{iso}", file=f)
        print(f"SET,shutter_speed,{shutter_speed}", file=f)
        # Set actuators at random + take image
        rng = np.random.default_rng(seed)
        red = betabinomial(0, 255, 5, 5, N, random_state=rng.integers(2**16))
        green = betabinomial(0, 255, 5, 5, N, random_state=rng.integers(2**16))
        blue = betabinomial(0, 255, 5, 5, N, random_state=rng.integers(2**16))
        pol_1 = betabinomial(-180, 180, 5, 5, N, random_state=rng.integers(2**16))
        pol_2 = betabinomial(-180, 180, 5, 5, N, random_state=rng.integers(2**16))
        for i in range(N):
            print("", file=f)
            # Set light source levels
            print(f"SET,red,{red[i]}", file=f)
            print(f"SET,green,{green[i]}", file=f)
            print(f"SET,blue,{blue[i]}", file=f)
            # Set polarizer angles
            print("SET,pol_1,%0.1f" % pol_1[i], file=f)
            print("SET,pol_2,%0.1f" % pol_2[i], file=f)
            # Measure
            print("MSR,1,0", file=f)
