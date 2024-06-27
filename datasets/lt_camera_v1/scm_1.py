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
Matrices for SCM 1.
"""

import numpy as np

# Note: W[j,i] != 0 encodes the edge i -> j
W = np.array(
    [
        [0.0, 0.0, 0.0, 0.0, 0.0],
        [0.98781118, 0.0, 0.0, 0.0, 0.72519297],
        [0.0, 0.96338249, 0.0, 0.0, 0.7217071],
        [0.61361936, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0],
    ]
)

D = np.array(
    [
        [0.19463871, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.96750973, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.47570493, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.31236664, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.13975248],
    ]
)
