# MIT License

# Copyright (c) 2025 Juan L. Gamella

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

# Obs. means
obs_means = np.array([0.0, 0.0, 0.0, 0.0, 0.0])

# Obs. variances
obs_vars = np.array([1.3855493, 1.16426732, 1.00502177, 1.95646855, 1.27482347])

# Intervention means
int_means = np.array([1.16920556, 1.47496736, -1.60596209, -1.96578519, 1.0117071])

# Intervention variances
int_vars = np.array([1.94878138, 1.35886756, 1.57343313, 1.1021785, 1.30511067])
