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
Lists with the ground-truth intervention targets in each regime of the regime_jumps_* experiments.
"""

# Intervention targets for "regime_jumps_single"
# (32 regimes)
targets_single = [
    [],
    ["v_2"],
    [],
    ["res_out"],
    ["v_out"],
    ["hatch"],
    ["v_1"],
    ["osr_upwind"],
    [],
    ["osr_upwind"],
    ["v_out"],
    ["v_1"],
    ["res_in"],
    ["osr_upwind"],
    ["res_out"],
    ["osr_downwind"],
    ["osr_ambient"],
    ["v_in"],
    ["hatch"],
    ["osr_upwind"],
    [],
    ["res_in"],
    ["v_1"],
    ["osr_intake"],
    [],
    ["v_1"],
    [],
    ["osr_upwind"],
    ["osr_intake"],
    ["osr_ambient"],
    ["v_in"],
    ["res_in"],
]

# Intervention targets for "regime_jumps_multi"
# (32 regimes)
targets_multi = [
    [],
    [],
    ["v_in", "res_out", "res_in", "hatch"],
    ["hatch", "v_in", "v_1"],
    ["v_out", "v_1", "res_out", "osr_downwind", "osr_ambient"],
    ["v_out", "osr_upwind", "osr_ambient", "v_2"],
    ["res_out", "osr_downwind", "osr_upwind", "v_out"],
    ["v_in", "osr_downwind", "res_out", "osr_upwind", "v_2"],
    ["osr_upwind", "v_1", "osr_intake"],
    ["hatch"],
    ["v_1", "osr_downwind", "v_in"],
    ["hatch", "v_1", "res_in"],
    ["hatch"],
    [],
    [],
    ["res_in", "v_out", "osr_ambient", "v_2", "osr_downwind"],
    [],
    ["res_out", "osr_ambient", "osr_downwind", "osr_intake", "v_out"],
    ["v_2", "v_in", "v_out", "osr_intake"],
    ["osr_downwind", "osr_upwind", "res_in", "osr_ambient", "v_1"],
    ["v_in", "hatch"],
    [],
    ["v_2", "hatch"],
    [],
    ["res_out", "v_in", "v_2", "v_1"],
    [],
    ["v_out", "osr_upwind", "v_2", "res_in"],
    ["v_in", "osr_ambient"],
    ["v_1"],
    [],
    [],
    ["v_in", "v_1"],
]
