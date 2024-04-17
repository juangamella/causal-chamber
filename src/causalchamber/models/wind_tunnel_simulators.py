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

"""Simulators of the downwind barometer pressure given time-series of
the loads and hatch positions (shown in Fig. 6f of the
manuscript). See Appendix D1 of the manuscript for more details.

"""

import numpy as np
from .wind_tunnel_models import model_a1, model_a2, model_c2, model_c3


def simulator_a1_c2(
    # Input
    load_in,
    load_out,
    hatch,
    P_amb,
    # Parameters for model A1
    L_min,
    omega_max,
    # Parameters for model C2
    S_max,
    Q_max,
    r,
    # Sensor noise
    barometer_error,  # The barometer offset
    barometer_precision,  # The std. of the barometer sensor noise
    random_state=42,
):
    load_in, load_out = np.array(load_in), np.array(load_out)
    omega_in = model_a1(load_in, L_min, omega_max)
    omega_out = model_a1(load_out, L_min, omega_max)
    P_dw = model_c2(omega_in, omega_out, P_amb, S_max, omega_max, Q_max, r)
    rng = np.random.default_rng(random_state)
    P_dw += rng.normal(barometer_error, barometer_precision, size=len(P_dw))
    return P_dw, omega_in, omega_out


def simulator_a1_c3(
    # Input
    load_in,
    load_out,
    hatch,
    P_amb,
    # Parameters for model A1
    L_min,
    omega_max,
    # Parameters for model C3
    S_max,
    Q_max,
    r_0,
    beta,
    # Sensor noise
    barometer_error,  # The barometer offset
    barometer_precision,  # The std. of the barometer sensor noise
    random_state=42,
):
    load_in, load_out = np.array(load_in), np.array(load_out)
    omega_in = model_a1(load_in, L_min, omega_max)
    omega_out = model_a1(load_out, L_min, omega_max)
    P_dw = model_c3(
        omega_in, omega_out, hatch, P_amb, S_max, omega_max, Q_max, r_0, beta
    )
    rng = np.random.default_rng(random_state)
    P_dw += rng.normal(barometer_error, barometer_precision, size=len(P_dw))
    return P_dw, omega_in, omega_out


def simulator_a2_c3(
    # Input
    load_in,
    load_out,
    hatch,
    P_amb,
    # Parameters for model A1
    I,
    tau,
    C,
    timestamps,
    omega_in_0,
    omega_out_0,
    # Parameters for model C3
    S_max,
    omega_max,
    Q_max,
    r_0,
    beta,
    # Sensor noise
    barometer_error,  # The barometer offset
    barometer_precision,  # The std. of the barometer sensor noise
    random_state=42,
    # For the ODE solver of model a2
    simulation_steps=100,
):
    load_in, load_out = np.array(load_in), np.array(load_out)
    omega_in = model_a2(load_in, I, tau, C, omega_in_0, timestamps, simulation_steps)
    omega_out = model_a2(load_out, I, tau, C, omega_out_0, timestamps, simulation_steps)
    P_dw = model_c3(
        omega_in, omega_out, hatch, P_amb, S_max, omega_max, Q_max, r_0, beta
    )
    rng = np.random.default_rng(random_state)
    P_dw += rng.normal(barometer_error, barometer_precision, size=len(P_dw))
    return P_dw, omega_in, omega_out
