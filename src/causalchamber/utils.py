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
Wildcard module for utility functions.
"""

import numpy as np

# --------------------------------------------------------------------
# Functions to manipulate the ground truth graphs


def edges_to_adjacency(edges, variables):
    """Given edges encoded as a list of tuples, i.e. (from,to), encode as
    an adjacency matrix where `A[from,to] != 0` implies `from -> to`.
    """
    p = len(variables)
    idx = dict(zip(variables, range(p)))
    A = np.zeros((p, p))
    for fro, to in edges:
        if fro in variables and to in variables:
            fro = idx[fro]
            to = idx[to]
            A[fro, to] = 1
    return A


def points_on_circle(n, radius=1):
    """
    Coordinates of n equidistant points on a circle of given radius centered at (0,0).
    """
    theta = np.linspace(0, 2 * np.pi, n + 1)
    x = np.sin(theta)[:-1]
    y = np.cos(theta)[:-1]
    points = list(zip(x, y))
    points.reverse()
    return points


def graph_to_tikz(
    A, points=None, radius=1, labels=None, spaces=4, bend=None, undirected=False
):
    """
    Transform an adjacency matrix A, where `A[i,j] != 0` implies `i -> j` into a latex tikz graph.
    """
    p = len(A)
    if points is None:
        points = points_on_circle(p, radius)
    if labels is None:
        labels = ["$X_{%d}$" % i for i in range(p)]
    indent = " " * spaces
    string = indent + "\\begin{tikzpicture}" + "\n"
    # Add nodes
    for j, (x, y) in enumerate(points):
        string += (
            indent
            + "    \\node[circle, inner sep=0.12em] (%d) at (%0.3f, %0.3f) {%s};\n"
            % (j, x * radius, y * radius, labels[j])
        )
    # Add edges
    string += indent + "    \\begin{scope}[]" + "\n"
    for j, row in enumerate(A):
        for i in np.where(row != 0)[0]:
            if undirected and A[i, j] != 0:
                tip = "-, %s" % undirected
            else:
                tip = "->"
            if bend is None:
                string += indent + "        \\draw[%s] (%d) edge (%d);\n" % (tip, j, i)
            else:
                jj, ii = 0, (i - j) % p
                direction = "left" if (ii - jj) < p / 2 else "right"
                amount = abs(bend * (1 - (ii - jj) / p * 2))
                bend_str = "bend %s=%d" % (direction, amount)
                string += indent + "        \\draw[%s, %s] (%d) edge (%d);\n" % (
                    tip,
                    bend_str,
                    j,
                    i,
                )
    string += indent + "    \\end{scope}" + "\n"
    string += indent + "\\end{tikzpicture}" + "\n"
    return string
