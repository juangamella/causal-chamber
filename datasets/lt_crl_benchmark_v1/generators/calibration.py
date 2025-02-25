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

- calibration

"""

# Where the generated .txt protocol files are saved
OUTPUT_DIR = "./protocols"

# Dictionary with the exogenous variables and their zero-levels
exogenous_zeros = {
    "l_11": 0,
    "l_12": 0,
    "l_21": 0,
    "l_22": 0,
    "l_31": 0,
    "l_32": 0,
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

N = 10  # measurements per actuator setting

rng = np.random.default_rng(7600688198727512)
actuators = pd.DataFrame(
    {
        "flag": np.zeros(N),
        "red": rng.uniform(0, 255, size=N),
        "green": rng.uniform(0, 255, size=N),
        "blue": rng.uniform(0, 255, size=N),
        "pol_1": rng.uniform(-90, 90, size=N),
        "pol_2": rng.uniform(-90, 90, size=N),
    }
)

assert len(actuators) == N

# ----------------------------
protocol_name = "calibration.txt"
actuators.to_csv(f"/tmp/{protocol_name}", index=False)

# Write to protocol
filename = f"{OUTPUT_DIR}/{protocol_name}"
with open(filename, "w") as f:
    print("# Setup", file=f)
    # Set all actuators to their zero value
    for e, zero in exogenous_zeros.items():
        print(f"SET,{e},{zero}", file=f)

    # First, generate an array with the color combitions: only red,
    # only green, only blue, and random colors
    # Divide the color space {0...255} into 64 steps
    color_steps = np.linspace(0, 255, 64).astype(int)
    color_settings = []
    # Pure colors
    for i in range(3):
        for_this_color = np.zeros((len(color_steps), 4))
        for_this_color[:, 0] = i  # set flag
        for_this_color[:, i + 1] = color_steps  # Set color steps
        color_settings.append(for_this_color)
    # Random colors
    random_colors = rng.choice(np.arange(256).astype(int), replace=True, size=(64, 4))
    random_colors[:, 0] = 3  # set flag
    color_settings.append(random_colors)
    # Combine, tile and shuffle
    color_settings = np.vstack(color_settings)
    color_settings = np.tile(color_settings, reps=(N, 1))
    rng.shuffle(color_settings, axis=0)

    # Iterate over color combinations for each polarizer position
    for pol_1 in np.linspace(0, 90, 4):
        print(f"\n\nSET,pol_1,{pol_1:0.1f}", file=f)
        for flag, red, green, blue in color_settings:
            print("", file=f)
            print(f"SET,flag,{int(flag)}", file=f)
            print(f"SET,red,{int(red)}", file=f)
            print(f"SET,green,{int(green)}", file=f)
            print(f"SET,blue,{int(blue)}", file=f)

            # Measure
            print("MSR,1,0", file=f)
