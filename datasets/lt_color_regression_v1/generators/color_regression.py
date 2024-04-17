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
Generates the experiment protocols for the experiments:

- reference
- bright_colors
- pol_1_90
- aperture_11.0
- shutter_speed_0.001
- iso_1000.0


"""

import numpy as np

# Where the generated .txt protocol files are saved
OUTPUT_DIR = "./protocols"

# Generation parameters
N = 10000

# Dictionary with the exogenous variables and their zero-levels
exogenous_zeros = {
    "red": 0,
    "green": 0,
    "blue": 0,
    "pol_1": 0,
    "pol_2": 0,
    "l_11": 0,
    "l_12": 0,
    "l_21": 0,
    "l_22": 0,
    "l_31": 0,
    "l_32": 0,
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
    "osr_angle_1": 1,
    "osr_angle_2": 1,
    "osr_c": 1,
    "v_angle_1": 5,
    "v_angle_2": 5,
    "v_c": 5,
    "camera": 1,
    "aperture": "1.8",
    "iso": "100",
    "shutter_speed": "1/200",
}

rng = np.random.default_rng(1)

# Experiments: reference and bright_colors
for experiment in ["reference", "bright_colors"]:
    protocol_name = f"{experiment}.txt"
    print(f"  {protocol_name}")
    filename = f"{OUTPUT_DIR}/{protocol_name}"
    with open(filename, "w") as f:
        # Set all actuators to their zero value
        for e, zero in exogenous_zeros.items():
            print(f"SET,{e},{zero}", file=f)
        for i in range(N):
            # Set light source levels
            print("", file=f)
            mmin, mmax = (0, 128) if experiment == "reference" else (128, 256)
            print(f"SET,red,{rng.integers(mmin,mmax)}", file=f)
            print(f"SET,green,{rng.integers(mmin,mmax)}", file=f)
            print(f"SET,blue,{rng.integers(mmin,mmax)}", file=f)
            # Take a measurement
            print("MSR,1,0", file=f)


# All other experiments
def to_number(param):
    """Transform a camera parameter (e.g. ISO, f-stop (aperture) or
    shutter speed) from string into a float.

    Examples
    --------
    >>> to_number("1/200")
    0.005
    >>> to_number('3"')
    180.0
    >>> to_number('1.8')
    1.8
    >>> to_number('22')
    22.0
    >>> to_number(45)
    45
    """
    if type(param) == int:
        return param
    elif param[-1] == '"':
        return float(eval(param[:-1]) * 60)
    else:
        return float(eval(param))


interventions = {
    "pol_1": [45, 90],
    "aperture": ["5.0", "11"],
    "shutter_speed": ["1/500", "1/1000"],  # 0.002 and 0.001
    "iso": ["500", "1000"],
}

# interventions = {
#     "pol_1": [90],
#     "aperture": ["11"],
#     "shutter_speed": ["1/1000"],  # 0.002 and 0.001
#     "iso": ["1000"],
# }

for target, values in interventions.items():
    for value in values:
        protocol_name = f"{target}_{to_number(value)}.txt"
        print(f"  {protocol_name}")
        filename = f"{OUTPUT_DIR}/{protocol_name}"

        with open(filename, "w") as f:
            # Set target to its value and other actuators to their zero level
            for e, zero in exogenous_zeros.items():
                if e == target:
                    print(f"SET,{target},{value}", file=f)
                else:
                    print(f"SET,{e},{zero}", file=f)
            # Iterate through colors
            for i in range(N):
                # Set light source levels
                print("", file=f)
                print(f"SET,red,{rng.integers(0,128)}", file=f)
                print(f"SET,green,{rng.integers(0,128)}", file=f)
                print(f"SET,blue,{rng.integers(0,128)}", file=f)
                # Take a measurement
                print("MSR,1,0", file=f)
