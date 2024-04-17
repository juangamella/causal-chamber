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

"""This module defines the variables and ground-truth edges/graphs
for each chamber configuration. The `latex_name` function allows you
to go from the column name of a variable to its latex expression used
in the original paper (TODO).

"""

import pandas as pd
import numpy as np

# --------------------------------------------------------------------
# Definition of variables and latex names

_variables_lt_standard = [
    "red",
    "green",
    "blue",
    "osr_c",
    "v_c",
    "current",
    "pol_1",
    "pol_2",
    "osr_angle_1",
    "osr_angle_2",
    "v_angle_1",
    "v_angle_2",
    "angle_1",
    "angle_2",
    "ir_1",
    "vis_1",
    "ir_2",
    "vis_2",
    "ir_3",
    "vis_3",
    "l_11",
    "l_12",
    "l_21",
    "l_22",
    "l_31",
    "l_32",
    "diode_ir_1",
    "diode_vis_1",
    "diode_ir_2",
    "diode_vis_2",
    "diode_ir_3",
    "diode_vis_3",
    "t_ir_1",
    "t_vis_1",
    "t_ir_2",
    "t_vis_2",
    "t_ir_3",
    "t_vis_3",
]

_variables_lt_camera = _variables_lt_standard + [
    "im",
    "aperture",
    "shutter_speed",
    "iso",
]

_variables_wt_standard = [
    "hatch",
    "pot_1",
    "pot_2",
    "osr_1",
    "osr_2",
    "osr_mic",
    "osr_in",
    "osr_out",
    "osr_upwind",
    "osr_downwind",
    "osr_ambient",
    "osr_intake",
    "v_1",
    "v_2",
    "v_mic",
    "v_in",
    "v_out",
    "load_in",
    "load_out",
    "current_in",
    "current_out",
    "res_in",
    "res_out",
    "rpm_in",
    "rpm_out",
    "pressure_upwind",
    "pressure_downwind",
    "pressure_ambient",
    "pressure_intake",
    "mic",
    "signal_1",
    "signal_2",
]

_variables_wt_pressure_control = _variables_wt_standard

_latex_names = {
    # Light tunnel variables
    "red": r"R",
    "green": r"G",
    "blue": r"B",
    "osr_c": r"O_C",
    "v_c": r"R_C",
    "current": r"\tilde{C}",
    "pol_1": r"\theta_1",
    "pol_2": r"\theta_2",
    "osr_angle_1": r"O_1",
    "osr_angle_2": r"O_2",
    "v_angle_1": r"R_1",
    "v_angle_2": r"R_2",
    "angle_1": r"\tilde{\theta}_1",
    "angle_2": r"\tilde{\theta}_2",
    "ir_1": r"\tilde{I}_1",
    "vis_1": r"\tilde{V}_1",
    "ir_2": r"\tilde{I}_2",
    "vis_2": r"\tilde{V}_2",
    "ir_3": r"\tilde{I}_3",
    "vis_3": r"\tilde{V}_3",
    "l_11": r"L_{11}",
    "l_12": r"L_{12}",
    "l_21": r"L_{21}",
    "l_22": r"L_{22}",
    "l_31": r"L_{31}",
    "l_32": r"L_{32}",
    "diode_ir_1": r"D^I_1",
    "diode_vis_1": r"D^V_1",
    "diode_ir_2": r"D^I_2",
    "diode_vis_2": r"D^V_2",
    "diode_ir_3": r"D^I_3",
    "diode_vis_3": r"D^V_3",
    "t_ir_1": r"T^I_1",
    "t_vis_1": r"T^V_1",
    "t_ir_2": r"T^I_2",
    "t_vis_2": r"T^V_2",
    "t_ir_3": r"T^I_3",
    "t_vis_3": r"T^V_3",
    "im": r"\tilde{\text{I}}\text{m}",
    "shutter_speed": r"T_\text{Im}",
    "aperture": r"\text{Ap}",
    "iso": r"\text{ISO}",
    # Wind tunnel variables
    "hatch": r"H",
    "pot_1": r"A_1",
    "pot_2": r"A_2",
    "osr_1": r"O_1",
    "osr_2": r"O_2",
    "osr_mic": r"O_M",
    "osr_in": r"O_\text{in}",
    "osr_out": r"O_\text{out}",
    "osr_upwind": r"O_\text{up}",
    "osr_downwind": r"O_\text{dw}",
    "osr_ambient": r"O_\text{amb}",
    "osr_intake": r"O_\text{int}",
    "v_1": r"R_1",
    "v_2": r"R_2",
    "v_mic": r"R_M",
    "v_in": r"R_\text{in}",
    "v_out": r"R_\text{out}",
    "load_in": r"L_\text{in}",
    "load_out": r"L_\text{out}",
    "current_in": r"\tilde{C}_\text{in}",
    "current_out": r"\tilde{C}_\text{out}",
    "res_in": r"T_\text{in}",
    "res_out": r"T_\text{out}",
    "rpm_in": r"\tilde{\omega}_\text{in}",
    "rpm_out": r"\tilde{\omega}_\text{out}",
    "pressure_upwind": r"\tilde{P}_\text{up}",
    "pressure_downwind": r"\tilde{P}_\text{dw}",
    "pressure_ambient": r"\tilde{P}_\text{amb}",
    "pressure_intake": r"\tilde{P}_\text{int}",
    "mic": r"\tilde{M}",
    "signal_1": r"\tilde{S}_1",
    "signal_2": r"\tilde{S}_2",
}


# --------------------------------------------------------------------
# Definition of ground truth edges


_edges_lt_standard = [
    ("red", "ir_1"),
    ("green", "ir_1"),
    ("blue", "ir_1"),
    ("red", "ir_2"),
    ("green", "ir_2"),
    ("blue", "ir_2"),
    ("red", "ir_3"),
    ("green", "ir_3"),
    ("blue", "ir_3"),
    ("red", "vis_1"),
    ("green", "vis_1"),
    ("blue", "vis_1"),
    ("red", "vis_2"),
    ("green", "vis_2"),
    ("blue", "vis_2"),
    ("red", "vis_3"),
    ("green", "vis_3"),
    ("blue", "vis_3"),
    ("red", "current"),
    ("green", "current"),
    ("blue", "current"),
    ("pol_1", "ir_3"),
    ("pol_2", "ir_3"),
    ("pol_1", "vis_3"),
    ("pol_2", "vis_3"),
    ("pol_1", "angle_1"),
    ("pol_2", "angle_2"),
    ("v_angle_1", "angle_1"),
    ("osr_angle_1", "angle_1"),
    ("v_angle_2", "angle_2"),
    ("osr_angle_2", "angle_2"),
    ("v_c", "current"),
    ("osr_c", "current"),
    ("l_11", "ir_1"),
    ("l_12", "ir_1"),
    ("l_11", "vis_1"),
    ("l_12", "vis_1"),
    ("t_ir_1", "ir_1"),
    ("diode_ir_1", "ir_1"),
    ("t_vis_1", "vis_1"),
    ("diode_vis_1", "vis_1"),
    ("l_21", "ir_2"),
    ("l_22", "ir_2"),
    ("l_21", "vis_2"),
    ("l_22", "vis_2"),
    ("t_ir_2", "ir_2"),
    ("diode_ir_2", "ir_2"),
    ("t_vis_2", "vis_2"),
    ("diode_vis_2", "vis_2"),
    ("l_31", "ir_3"),
    ("l_32", "ir_3"),
    ("l_31", "vis_3"),
    ("l_32", "vis_3"),
    ("t_ir_3", "ir_3"),
    ("diode_ir_3", "ir_3"),
    ("t_vis_3", "vis_3"),
    ("diode_vis_3", "vis_3"),
]

_edges_lt_camera = _edges_lt_standard + [
    ("pol_1", "im"),
    ("pol_2", "im"),
    ("red", "im"),
    ("green", "im"),
    ("blue", "im"),
    ("shutter_speed", "im"),
    ("aperture", "im"),
    ("iso", "im"),
]

_edges_wt_standard = [
    ("load_in", "rpm_in"),
    ("res_in", "rpm_in"),
    ("load_in", "rpm_out"),
    ("load_in", "current_in"),
    ("load_in", "current_out"),
    ("load_out", "rpm_in"),
    ("load_out", "rpm_out"),
    ("res_out", "rpm_out"),
    ("load_out", "current_out"),
    ("load_out", "current_in"),
    ("hatch", "rpm_in"),
    ("hatch", "rpm_out"),
    ("load_in", "pressure_intake"),
    ("hatch", "pressure_intake"),
    ("load_out", "pressure_intake"),
    ("osr_intake", "pressure_intake"),
    ("load_in", "pressure_upwind"),
    ("hatch", "pressure_upwind"),
    ("load_out", "pressure_upwind"),
    ("osr_upwind", "pressure_upwind"),
    ("load_in", "pressure_downwind"),
    ("hatch", "pressure_downwind"),
    ("load_out", "pressure_downwind"),
    ("osr_downwind", "pressure_downwind"),
    ("osr_ambient", "pressure_ambient"),
    ("osr_in", "current_in"),
    ("v_in", "current_in"),
    ("osr_out", "current_out"),
    ("v_out", "current_out"),
    ("pot_1", "signal_1"),
    ("osr_1", "signal_1"),
    ("v_1", "signal_1"),
    ("pot_1", "signal_2"),
    ("pot_2", "signal_2"),
    ("osr_2", "signal_2"),
    ("v_2", "signal_2"),
    ("pot_1", "mic"),
    ("load_in", "mic"),
    ("load_out", "mic"),
    ("hatch", "mic"),
    ("osr_mic", "mic"),
    ("v_mic", "mic"),
]

_edges_wt_pressure_control = _edges_wt_standard + [
    ("pressure_downwind", "load_in"),
    ("pressure_downwind", "load_out"),
]

# --------------------------------------------------------------------
# Public API of the module


def latex_name(var, enclose=True):
    """
    Obtain a variable's LaTeX name from its name as it appears in the columns of the .csv files in datasets.

    Parameters
    ----------
    var : str
        The variable name as it appears in dataset columns.
    enclose : bool, optional
        If True, encloses the LaTeX name in dollar signs. Default is True.

    Returns
    -------
    str
        The LaTeX-formatted name of the variable as given in the original paper.

    """
    if var not in _latex_names:
        return var
    else:
        name = _latex_names[var]
        return "$" + name + "$" if enclose else name


def variables(chamber, configuration):
    """
    Return the variables provided by the given chamber in the given configuration.

    Parameters
    ----------
    chamber : str
        The chamber e.g., 'lt' for the light tunnel, 'wt' for the wind tunnel.
    configuration : str
        The configuration of the chamber. e.g., 'standard', 'camera', 'pressure-control'.

    Returns
    -------
    list
        A list of variables relevant to the specified chamber and configuration.

    Raises
    ------
    ValueError
        If the chamber/configuration combination is unknown.

    >>> len(variables('lt', 'standard'))
    38
    >>> len(variables('lt', 'camera'))
    42
    >>> len(variables('wt', 'standard'))
    32
    >>> len(variables('wt', 'pressure-control'))
    32

    """
    if chamber == "lt" and configuration == "standard":
        return _variables_lt_standard
    if chamber == "lt" and configuration == "camera":
        return _variables_lt_camera
    elif chamber == "wt" and configuration == "standard":
        return _variables_wt_standard
    elif chamber == "wt" and configuration == "pressure-control":
        return _variables_wt_pressure_control
    else:
        raise ValueError(f"Unknown chamber/configuration: {chamber}/{configuration}")


def edges(chamber, configuration):
    """
    Return the edges in the ground truth graph of the given chamber in the given configuration.

    Parameters
    ----------
    chamber : str
        The chamber e.g., 'lt' for the light tunnel, 'wt' for the wind tunnel.
    configuration : str
        The configuration of the chamber. e.g., 'standard', 'camera', 'pressure-control'.

    Returns
    -------
    list of tuples
        A list of tuples representing the edges in the ground truth graph for the specified chamber and configuration. A tuple `(i,j)` denotes the edge `i -> j`.

    Raises
    ------
    ValueError
        If the chamber/configuration combination is unknown.

    >>> len(edges('lt', 'standard'))
    57
    >>> len(edges('lt', 'camera'))
    65
    >>> len(edges('wt', 'standard'))
    42
    >>> len(edges('wt', 'pressure-control'))
    44

    """
    if chamber == "lt" and configuration == "standard":
        return _edges_lt_standard
    if chamber == "lt" and configuration == "camera":
        return _edges_lt_camera
    elif chamber == "wt" and configuration == "standard":
        return _edges_wt_standard
    elif chamber == "wt" and configuration == "pressure-control":
        return _edges_wt_pressure_control
    else:
        raise ValueError(f"Unknown chamber/configuration: {chamber}/{configuration}")


def graph(chamber, configuration):
    """
    Return the adjacency matrix of the ground truth graph of the given chamber in the given configuration.

    Parameters
    ----------
    chamber : str
        The chamber e.g., 'lt' for the light tunnel, 'wt' for the wind tunnel.
    configuration : str
        The configuration of the chamber. g.g., 'standard', 'camera', 'pressure-control'.

    Returns
    -------
    DataFrame
        A pandas DataFrame representing the adjacency matrix of the graph, with variables as both index and columns. An entry `[from,to] != 1` denotes the edge `from -> to`.

    >>> graph('lt', 'standard').values.sum()
    57
    >>> graph('lt', 'camera').values.sum()
    65
    >>> graph('wt', 'standard').values.sum()
    42
    >>> graph('wt', 'pressure-control').values.sum()
    44

    """
    nodes = variables(chamber, configuration)
    p = len(nodes)
    idx = dict(zip(nodes, np.arange(p)))
    adjacency = np.zeros((p, p), dtype=int)
    for fro, to in edges(chamber, configuration):
        adjacency[idx[fro], idx[to]] = 1
    return pd.DataFrame(adjacency, index=nodes, columns=nodes)


# ----------------------------------------------------------------------
# Doctests
if __name__ == "__main__":
    import doctest

    # Check consistency between graphs and variables
    assert set(graph("lt", "standard").columns) == set(variables("lt", "standard"))
    assert set(graph("lt", "standard").index) == set(variables("lt", "standard"))

    assert set(graph("lt", "camera").columns) == set(variables("lt", "camera"))
    assert set(graph("lt", "camera").index) == set(variables("lt", "camera"))

    assert set(graph("wt", "standard").columns) == set(variables("wt", "standard"))
    assert set(graph("wt", "standard").index) == set(variables("wt", "standard"))

    assert set(graph("wt", "pressure-control").columns) == set(
        variables("wt", "pressure-control")
    )

    doctest.testmod(
        extraglobs={},
        verbose=True,
        optionflags=doctest.ELLIPSIS,
    )
