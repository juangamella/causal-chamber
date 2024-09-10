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

# Weights matrix
W = np.array(
    [
        [0.0, 0.0, 0.0, 0.0, 0.0],
        [0.71943922, 0.0, 0.0, 0.0, 0.67726298],
        [0.0, 0.89303215, 0.0, 0.0, 0.98534901],
        [0.84868401, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0],
    ]
)
# Noise scale
D = np.array(
    [
        [0.19463871, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.96750973, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.47570493, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.31236664, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.13975248],
    ]
)
# Observational means
obs_means = np.array([0.3773956, 0.34388784, 0.38585979, 0.3697368, 0.30941773])
# Standard deviations
stds = np.array([0.09926867, 0.09283419, 0.09358193, 0.07384341, 0.08351158])

# Interventional means
int_means = np.array([0.48110359, 0.45315549, 0.49229844, 0.47796442, 0.41385188])
