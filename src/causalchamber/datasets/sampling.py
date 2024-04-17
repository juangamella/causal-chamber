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
Functions for general sampling.
"""

import numpy as np


def random_walk(n, step_size=1, step_resolution=1, random_state=None):
    rng = np.random.default_rng(random_state)
    possible_transitions = np.arange(
        -step_size, step_size + step_resolution, step_resolution
    )
    steps = rng.choice(possible_transitions, size=n, replace=True)
    return np.cumsum(steps)


def random_walk_mirrored(
    n, minn, maxx, step_size=1, step_resolution=1, random_state=None
):
    rng = np.random.default_rng(random_state - 1)
    init = rng.choice(np.arange(minn, maxx + step_resolution, step_resolution))
    walk = init + random_walk(
        n,
        step_size=step_size,
        step_resolution=step_resolution,
        random_state=random_state,
    )
    # As long as walk is out of bounds
    while (
        maxx is not None
        and (walk > maxx).any()
        or minn is not None
        and (walk < minn).any()
    ):
        walk = np.minimum(walk, maxx) - np.maximum(walk, maxx) + maxx
        walk = np.maximum(walk, minn) - np.minimum(walk, minn) + minn
    return walk


# Deprecatedx
def discrete_rw(n, minn, maxx, step_sizes=[-1, 0, 1], p=None, seed=42):
    rng = np.random.default_rng(seed)
    walk = np.zeros(n)
    walk[0] = rng.integers(minn, maxx + 1)
    steps = rng.choice(step_sizes, p=p, size=n - 1, replace=True)
    for i, s in enumerate(steps):
        walk[i + 1] = min(max(walk[i] + s, minn), maxx)
    return walk


def smooth_discrete_rw(n, minn, maxx, step_sizes=[-1, 0, 1], p=None, lags=0, seed=42):
    walk = discrete_rw(n + lags, minn, maxx, step_sizes, p, seed)
    walk = pd.DataFrame(walk).rolling(lags).mean()[lags:]
    return walk.values
