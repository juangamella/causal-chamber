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
import pandas as pd

"""
Generates the experiment protocols for the experiments:

- citris_1

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


# ----------------------------
# Generate actuator inputs

N = int(1e5)
burn_in = 1000


def reflect(x, lo, hi):
    if x < lo:
        return 2 * lo - x
    elif x > hi:
        return 2 * hi - x
    else:
        return x


rng = np.random.default_rng(1297781987260068)
df = pd.DataFrame(
    np.zeros((N + burn_in, 6)),
    columns=["flag", "red", "green", "blue", "pol_1", "pol_2"],
)

no_int = 0.35
flag = rng.choice(
    np.arange(6), replace=True, p=[no_int] + [(1 - no_int) / 5] * 5, size=N
)
flag = np.concatenate([np.zeros(burn_in), flag])

df.flag = flag

for i in range(1, N + burn_in):
    prev = df.iloc[i - 1]

    # red: random walk
    if df.iloc[i].flag == 1:
        red = rng.uniform(0, 255)
    else:
        red = prev.red + rng.uniform(-50, 50)
    df.at[i, "red"] = reflect(red, 0, 255)

    # green: takes steps towards red
    if df.iloc[i].flag == 2:
        green = rng.uniform(0, 255)
    else:
        green = prev.green + (prev.red - prev.green) / 2 + rng.uniform(-50, 50)
    df.at[i, "green"] = reflect(green, 0, 255)

    # blue: takes steps towards green
    if df.iloc[i].flag == 3:
        blue = rng.uniform(0, 255)
    else:
        blue = prev.blue + (prev.green - prev.blue) / 4 + rng.uniform(-50, 50)
    df.at[i, "blue"] = reflect(blue, 0, 255)

    # pol_1: random walk
    if df.iloc[i].flag == 4:
        pol_1 = rng.uniform(-90, 90)
    else:
        pol_1 = prev.pol_1 + rng.uniform(-10, 10)
    df.at[i, "pol_1"] = reflect(pol_1, -90, 90)

    # pol_2: takes steps towards pol_1 if blue > red, otherwise moves away from pol_1
    if df.iloc[i].flag == 5:
        pol_2 = rng.uniform(-90, 90)
    else:
        sign = 1 if blue > red else -1
        pol_2 = prev.pol_2 + sign * (prev.pol_1 - prev.pol_2) / 4 + rng.uniform(-5, 5)
    df.at[i, "pol_2"] = reflect(pol_2, -90, 90)

actuators = df.iloc[burn_in:]
assert len(actuators) == N

# ----------------------------
protocol_name = "citris_1.txt"
actuators.to_csv(f"/tmp/{protocol_name}", index=False)

# Write to protocol
filename = f"{OUTPUT_DIR}/{protocol_name}"
with open(filename, "w") as f:
    print("# Setup", file=f)
    # Set all actuators to their zero value
    for e, zero in exogenous_zeros.items():
        print(f"SET,{e},{zero}", file=f)

    # Set actuators and take image
    for flag, red, green, blue, pol_1, pol_2 in actuators.values:
        print("", file=f)
        print(f"SET,flag,{int(flag)}", file=f)
        print(f"SET,red,{int(red)}", file=f)
        print(f"SET,green,{int(green)}", file=f)
        print(f"SET,blue,{int(blue)}", file=f)
        print(f"SET,pol_1,{pol_1:0.1f}", file=f)
        print(f"SET,pol_2,{pol_2:0.1f}", file=f)
        # Measure
        print("MSR,1,0", file=f)
