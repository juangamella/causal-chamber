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
import itertools

"""
Generates the experiment protocols for the experiments:

- palette

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
}


colors = np.array(
    [
        # IBM color-blind safe palette
        [99, 142, 254],
        [119, 93, 239],
        [219, 37, 126],
        [253, 96, 0],
        [254, 175, 0],
        [254, 254, 254],
        # Nice(r) RGB
        [69, 111, 25],
        [15, 58, 125],
        [121, 4, 18],
        # Muted rainbow
        [178, 93, 166],
        [102, 136, 195],
        [72, 165, 106],
        [234, 175, 65],
        [206, 74, 74],
    ]
)

apertures = ["1.8", "11"]
isos = ["100", "1000"]
shutter_speeds = ["1/200", "1/1000"]

polarizer_angles = [0, 90]

protocol_name = f"palette.txt"
print(f"  {protocol_name}")
filename = f"{OUTPUT_DIR}/{protocol_name}"
with open(filename, "w") as f:
    # Set all actuators to their zero value
    for e, zero in exogenous_zeros.items():
        print(f"SET,{e},{zero}", file=f)
    # Iterate over all combinations
    for ap, iso, ss in itertools.product(apertures, isos, shutter_speeds):
        print(f"\n\nSET,aperture,{ap}", file=f)
        print(f"SET,iso,{iso}", file=f)
        print(f"SET,shutter_speed,{ss}", file=f)
        for pol_1 in polarizer_angles:
            print(f"SET,pol_1,{pol_1}", file=f)
            print("", file=f)
            for i, (r, g, b) in enumerate(colors):
                print(f"SET,flag,{i}", file=f)
                print(f"SET,red,{r}", file=f)
                print(f"SET,green,{g}", file=f)
                print(f"SET,blue,{b}", file=f)
                print("MSR,1,0", file=f)
