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
Generates the experiment protocols for the experiment:

- analog_calibration

"""

# Where the generated .txt protocol files are saved
OUTPUT_DIR = "./protocols"

# Dictionary with the exogenous variables and their zero-levels
exogenous_zeros = {
    "hatch": 0,
    "pot_1": 32,
    "pot_2": 32,
    "osr_1": 8,
    "osr_2": 8,
    "osr_in": 8,
    "osr_out": 8,
    "v_mic": 5,
    "osr_mic": 1,
    "osr_upwind": 8,
    "osr_intake": 8,
    "osr_ambient": 8,
    "osr_downwind": 8,
    "res_in": 1,
    "res_out": 1,
}

protocol_name = "analog_calibration.txt"
print(f"  {protocol_name}")
filename = f"{OUTPUT_DIR}/{protocol_name}"
with open(filename, "w") as f:
    # Set other exogenous variables
    for e, zero in exogenous_zeros.items():
        print(f"SET,{e},{zero}", file=f)

    # Test with 0 load on fans
    print("SET,flag,0", file=f)
    print("SET,load_in,0", file=f)
    print("SET,load_out,0", file=f)
    print("WAIT,5000", file=f)
    print("SET,v_in,1.1", file=f)
    print("SET,v_out,1.1", file=f)
    print("SET,v_1,1.1", file=f)
    print("SET,v_2,1.1", file=f)
    print("MSR,200,0", file=f)

    print("SET,v_in,2.56", file=f)
    print("SET,v_out,2.56", file=f)
    print("SET,v_1,2.56", file=f)
    print("SET,v_2,2.56", file=f)
    print("MSR,200,0", file=f)

    print("SET,v_in,5", file=f)
    print("SET,v_out,5", file=f)
    print("SET,v_1,5", file=f)
    print("SET,v_2,5", file=f)
    print("MSR,200,0", file=f)

    # Test with 0.01 load on fans
    print("SET,flag,1", file=f)
    print("SET,load_in,0.01", file=f)
    print("SET,load_out,0.01", file=f)
    print("WAIT,5000", file=f)
    print("SET,v_in,1.1", file=f)
    print("SET,v_out,1.1", file=f)
    print("SET,v_1,1.1", file=f)
    print("SET,v_2,1.1", file=f)
    print("MSR,200,0", file=f)

    print("SET,v_in,2.56", file=f)
    print("SET,v_out,2.56", file=f)
    print("SET,v_1,2.56", file=f)
    print("SET,v_2,2.56", file=f)
    print("MSR,200,0", file=f)

    print("SET,v_in,5", file=f)
    print("SET,v_out,5", file=f)
    print("SET,v_1,5", file=f)
    print("SET,v_2,5", file=f)
    print("MSR,200,0", file=f)
