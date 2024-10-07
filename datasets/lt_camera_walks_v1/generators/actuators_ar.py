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

- ar_1_uniform_ref
- ar_1_uniform_pol_1

"""


def sample_AR_1_uniform(n, coef, normalize=True, random_state=42):
    rng = np.random.default_rng(random_state)
    if isinstance(coef, tuple):
        coef = rng.uniform(coef[0], coef[1])
    innovations = rng.uniform(-1, 1, size=n)
    x = np.zeros_like(innovations)
    x[0] = innovations[0]
    for i in range(1, n):
        x[i] = x[i - 1] * coef + innovations[i]
    # Normalize: signal between -1 and 1
    if normalize:
        x -= x.min()
        x /= x.max()
        x = (2 * x) - 1
    return x


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

# Generation parameters
N = int(20e3)

# Parameters for the time series of each actuator in each experiment
all_settings = {
    "ref": {
        "red": (0.5, 128, 120),
        "green": (0.6, 128, 120),
        "blue": (0.7, 128, 120),
        "pol_1": (0.8, 0, 20),
        "pol_2": (0.9, 0, 20),
    },
    "pol_1": {
        "red": (0.5, 128, 120),
        "green": (0.6, 128, 120),
        "blue": (0.7, 128, 120),
        "pol_1": (0.8, 0, 20),
        "pol_2": (0.9, 90, 20),
    },
}

count = 0
for seed, (name, settings) in enumerate(all_settings.items()):
    protocol_name = f"ar_1_uniform_{name}.txt"
    filename = f"{OUTPUT_DIR}/{protocol_name}"
    print(f"  {protocol_name}")
    with open(filename, "w") as f:
        print("# Setup", file=f)
        # Set all actuators to their zero value
        for e, zero in exogenous_zeros.items():
            print(f"SET,{e},{zero}", file=f)

        # Sample actuator values
        values = {}
        for i, (var, (coef, mean, scale)) in enumerate(settings.items()):
            x = sample_AR_1_uniform(N, coef, random_state=i + 1728296067) * scale + mean
            values[var] = x

        # Set actuator values
        for i in range(N):
            print("", file=f)
            # Set light source levels
            print(f"SET,red,{int(values['red'][i])}", file=f)
            print(f"SET,green,{int(values['green'][i])}", file=f)
            print(f"SET,blue,{int(values['blue'][i])}", file=f)
            # Set polarizer angles
            print("SET,pol_1,%0.1f" % values["pol_1"][i], file=f)
            print("SET,pol_2,%0.1f" % values["pol_2"][i], file=f)
            # Measure
            print("MSR,1,0", file=f)
