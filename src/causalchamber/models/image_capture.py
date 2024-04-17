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


# --------------------------------------------------------------------
# Functions to draw the hexagon


def hexagon_vertices(center_x, center_y, radius, offset):
    vertices = []
    for angle in np.arange(0, 2 * np.pi, np.pi / 3):
        x = center_x + radius * np.cos(angle + offset)
        y = center_y + radius * np.sin(angle + offset)
        vertices.append([x, y])
    return np.array(vertices)


def coord_grid(image_size):
    X = np.tile(np.arange(image_size), (image_size, 1))
    Y = X.T[::-1, :]
    grid = np.array([X, Y])
    return np.transpose(grid, (1, 2, 0))


def hexagon_mask(center_x, center_y, radius, offset, image_size):
    mask = np.zeros((image_size, image_size))
    image_points = coord_grid(image_size)
    vertices = hexagon_vertices(center_x, center_y, radius, offset) * image_size
    # Compute cross products for a segment and all points
    cross_prods = []
    for i, vertex in enumerate(vertices):
        segment = vertex - vertices[(i + 1) % len(vertices)]
        vertex_to_points = image_points - vertex
        cross = np.cross(vertex_to_points, segment)
        cross_prods.append(cross)
    cross_prods = np.array(cross_prods)
    all_neg = (cross_prods <= 0).all(axis=0)
    all_pos = (cross_prods > 0).all(axis=0)
    mask = np.logical_or(all_neg, all_pos)
    return mask


# --------------------------------------------------------------
# Models


def model_f1(
    r,
    g,
    b,
    theta_1,
    theta_2,
    center_x,
    center_y,
    radius,
    offset,
    image_size,
):
    image = np.ones((3, image_size, image_size))
    theta_1, theta_2 = np.deg2rad(theta_1), np.deg2rad(theta_2)
    # Color
    image = np.zeros((3, image_size, image_size))
    malus_factor = np.cos(theta_1 - theta_2) ** 2
    image[0] = r * malus_factor
    image[1] = g * malus_factor
    image[2] = b * malus_factor
    # Apply hexagon mask
    mask = hexagon_mask(center_x, center_y, radius, offset, image_size)
    image *= mask
    return image.transpose((1, 2, 0)).astype(int)


def model_f2(
    r,
    g,
    b,
    theta_1,
    theta_2,
    S,
    w_r,
    w_g,
    w_b,
    exposure,
    center_x,
    center_y,
    radius,
    offset,
    image_size,
):
    # Transform parameters
    theta_1, theta_2 = np.deg2rad(theta_1), np.deg2rad(theta_2)
    r /= 255
    g /= 255
    b /= 255
    # Color
    malus_factor = np.cos(theta_1 - theta_2) ** 2
    W = np.diag([w_r, w_g, w_b])
    color = exposure * W @ S @ np.array([[r, g, b]]).T * malus_factor
    color = np.minimum(1, color)
    # Produce the image
    image = np.ones((3, image_size, image_size))
    image[0] *= color[0]
    image[1] *= color[1]
    image[2] *= color[2]
    mask = hexagon_mask(center_x, center_y, radius, offset, image_size)
    image *= mask
    return image.transpose((1, 2, 0))


def model_f3(
    r,
    g,
    b,
    theta_1,
    theta_2,
    S,
    w_r,
    w_g,
    w_b,
    exposure,
    Tp,
    Tc,
    center_x,
    center_y,
    radius,
    offset,
    image_size,
):
    # Transform parameters
    theta_1, theta_2 = np.deg2rad(theta_1), np.deg2rad(theta_2)
    r /= 255
    g /= 255
    b /= 255
    # Color
    malus_factor = (Tp - Tc) * np.cos(theta_1 - theta_2) ** 2 + Tc
    W = np.diag([w_r, w_g, w_b])
    color = exposure * W @ S @ np.array([[r, g, b]]).T * malus_factor
    color = np.minimum(1, color)
    # Produce the image
    image = np.ones((3, image_size, image_size))
    image[0] *= color[0]
    image[1] *= color[1]
    image[2] *= color[2]
    mask = hexagon_mask(center_x, center_y, radius, offset, image_size)
    image *= mask
    return image.transpose((1, 2, 0))
