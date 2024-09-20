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

- iso
- ap
- shutter_speed

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
        # Light off
        [0, 0, 0],
        # Whites
        [64, 64, 64],
        [128, 128, 128],
        [192, 192, 192],
        [255, 255, 255],
        # Reds
        [64, 0, 0],
        [128, 0, 0],
        [192, 0, 0],
        [255, 0, 0],
        # Greens
        [0, 64, 0],
        [0, 128, 0],
        [0, 192, 0],
        [0, 255, 0],
        # Blues
        [0, 0, 64],
        [0, 0, 128],
        [0, 0, 192],
        [0, 0, 255],
    ]
)

apertures = [
    "1.8",
    "2.0",
    "2.2",
    "2.5",
    "2.8",
    "3.2",
    "3.5",
    "4.0",
    "4.5",
    "5.0",
    "5.6",
    "6.3",
    "7.1",
    "8.0",
    "9.0",
    "10",
    "11",
    "13",
    "14",
    "16",
    "18",
    "20",
    "22",
]
ISOs = [
    "100",
    "125",
    "160",
    "200",
    "250",
    "320",
    "400",
    "500",
    "640",
    "800",
    "1000",
    "1250",
    "1600",
    "2000",
    "2500",
    "3200",
    "4000",
    "5000",
    "6400",
    "8000",
    "10000",
    "12800",
    "16000",
    "20000",
    "25600",
    "32000",
    "40000",
    "51200",
]
shutter_speeds = [
    "1/200",
    "1/250",
    "1/320",
    "1/400",
    "1/500",
    "1/640",
    "1/800",
    "1/1000",
    "1/1250",
    "1/1600",
    "1/2000",
    "1/2500",
    "1/3200",
    "1/4000",
]

parameters = list(
    zip(["aperture", "iso", "shutter_speed"], [apertures, ISOs, shutter_speeds])
)

for parameter, values in parameters:
    protocol_name = f"{parameter}.txt"
    print(f"  {protocol_name}")
    filename = f"{OUTPUT_DIR}/{protocol_name}"
    with open(filename, "w") as f:
        # Set all actuators to their zero value
        for e, zero in exogenous_zeros.items():
            print(f"SET,{e},{zero}", file=f)
        # Set other camera parameters to their zero value
        for p, v in parameters:
            if p == parameter:
                continue
            else:
                print(f"SET,{p},{v[0]}", file=f)
                # Iterate over parameter values and colors
        for v in values:
            print(f"\nSET,{parameter},{v}", file=f)
            for i, (r, g, b) in enumerate(colors):
                print(f"SET,flag,{i}", file=f)  # flag identifies the color
                print(f"SET,red,{r}", file=f)
                print(f"SET,green,{g}", file=f)
                print(f"SET,blue,{b}", file=f)
                print("MSR,1,0", file=f)
