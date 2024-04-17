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

"""This module contains the mechanistic models of the wind tunnel,
described in Appendix D, section 1 of the manuscript. The arguments to
the model_* functions below are named as in the manuscript; please
refer to it for details.

The simulators used for figure 6f are in the module simulators.py.

"""

import numpy as np


def model_a1(
    # Input
    L,
    # Parameters
    L_min,
    omega_max,
):
    """Model A1 of the steady-state fan speed given the load."""
    L = np.atleast_1d(L)
    omega = np.maximum(L, L_min) * omega_max
    omega[L == 0] = 0
    return omega if len(L) > 1 else omega[0]


def model_b1(
    # Input
    L,
    # Parameters
    C_min,
    C_max,
    L_min,
):
    """Model B1 of the drawn current given the load."""
    L = np.atleast_1d(L)
    C = C_min + np.maximum(L, L_min) ** 3 * (C_max - C_min)
    C[L == 0] = C_min
    return C if len(L) > 1 else C[0]


# Torque function \tau(L) defined in model A2, Appendix IV
# def tau(L, C_min, C_max, L_min, T):
#     L = np.atleast_1d(L)
#     torques = T * (C_min + np.maximum(L_min, L) ** 3 * (C_max - C_min) - C_min)
#     torques[L == 0] = 0
#     return torques if len(L) > 1 else torques[0]


def model_a2(
    # Input
    loads,
    # Parameters
    I,
    tau,
    K,
    # Parameters for the ODE solver
    omega_0,
    timestamps,
    simulation_steps=100,
    method="euler",
):
    """Model A2 of the fan-speed dynamics given a time-series of the fan
    load."""
    # Compute torque at each time point
    torques = tau(loads)

    # Compute speed at each time point by solving the ODE
    omegas = np.zeros_like(loads, dtype=float)
    omegas[0] = omega_0
    for i in range(1, len(loads)):
        timestep = timestamps[i] - timestamps[i - 1]
        torque = torques[i]
        if method == "euler":
            omega = omegas[i - 1]
            dt = timestep / simulation_steps
            for _ in range(simulation_steps):
                d_omega = 1 / I * (torque - K * omega**2)
                omega += dt * d_omega
            omegas[i] = omega
    return omegas


def model_c1(
    # Input
    omega_in,
    omega_out,
    P_amb,
    # Parameters
    S_max,
    omega_max,
):
    """Model C1 of the effect of the loads and hatch on the downwind barometer"""
    return (
        P_amb
        + S_max * (omega_in / omega_max) ** 2
        - S_max * (omega_out / omega_max) ** 2
    )


def model_c2(
    # Input
    omega_in,
    omega_out,
    P_amb,
    # Parameters
    S_max,
    omega_max,
    Q_max,
    r,
):
    """Model C2 of the effect of the loads and hatch on the downwind barometer"""
    S_r = lambda omega: _S_r(omega, r, Q_max, S_max, omega_max)
    return P_amb + S_r(omega_in) - S_r(omega_out)


def model_c3(
    # Input
    omega_in,
    omega_out,
    H,
    P_amb,
    # Parameters
    S_max,
    omega_max,
    Q_max,
    r_0,
    beta,
):
    """Model C3 of the effect of the loads and hatch on the downwind barometer"""
    # Compute impedance (airflow ratio) as a function of the hatch position H
    r = np.minimum(1, r_0 + beta * H / 45)
    S_rh = lambda omega: _S_r(omega, r, Q_max, S_max, omega_max)
    return P_amb + S_rh(omega_in) - S_rh(omega_out)


def _S_r(
    omega,
    r,
    Q_max,
    S_max,
    omega_max,
):
    """Used in models C2 and C3 to compute the static pressure produced by
    the fan, as the intersection of the impedance curve (for airflow
    ratio r) and the (linear) PQ-characteristic. See the manuscript for more details.

    """
    Z = S_max / Q_max**2 * (1 - r) / r**2
    # Find the intersection of the impedance curve S = ZQ^2 and the PQ-characteristic
    #   solve aQ^2 + bQ + c = 0 using the quadratic formula, where
    a = Z
    b = (omega / omega_max) * S_max / Q_max
    c = -((omega / omega_max) ** 2) * S_max
    # Intersection (Q,S)
    Q = (-b + np.sqrt(b**2 - 4 * a * c)) / 2 / a  # produced airflow
    S = Z * Q**2  # produced static pressure
    return S
