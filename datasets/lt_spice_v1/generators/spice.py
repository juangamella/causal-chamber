# MIT License

# Copyright (c) 2026 Silvan Vollmer, Juan L. Gamella

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

"""This python script uses the Causal Chamber® Remote Lab to collect
the data sets for SPICE (https://arxiv.org/abs/2604.09135) from the
Light Tunnel Mk2 (see https://docs.causalchamber.ai/).

NOTE: Replace the strings 'your_credentials_file' and
'your_chamber_id' in the code with your credentials file and the ID of
the chamber you have access to.

"""

# import packages
import causalchamber.lab as lab
import pandas as pd
import numpy as np
from scipy.stats import truncnorm

# help function
def sample_truncnorm_integers(n, mean, std, low, high, random_state=None):
    """Sample from a truncated normal distribution on [low, high].

    Parameters
    ----------
    n : int
        Number of samples.
    mean : float
        Mean of the underlying normal distribution.
    std : float
        Standard deviation of the underlying normal distribution.
    low : float
        Lower truncation bound.
    high : float
        Upper truncation bound.
    random_state : int or np.random.Generator, optional
        Random seed or generator.

    Returns
    -------
    ndarray
        Array of samples.
    """
    a = (low - mean) / std
    b = (high - mean) / std
    values = truncnorm.rvs(a, b, loc=mean, scale=std, size=n, random_state=random_state)
    return np.round(values).astype(int)

# connection to lab
rlab = lab.Lab(credentials_file = 'your_credentials_file')


""" 
Define experiment I (or II)
"""


N = 5500 # number of measurements per experiment (train + test)

rng = np.random.default_rng(23432)

# parameters
mean_green = 60
sd_green = 15

sps_current_ls_val = 4 # CHANGE TO 7 FOR EXPERIMENT II
mean_offset = 2950
slope_f2_val = 0.0624

M=20
experiment = rlab.new_experiment(chamber_id = 'your_chamber_id', config ='linked_leds')
for i in range(M):
    inputs = pd.DataFrame({
        'green': sample_truncnorm_integers(N, mean=mean_green, std=sd_green, low=0, high=255, random_state=rng),
        'sps_current_ls': np.repeat(sps_current_ls_val, N),
        'offset_current_ls': np.repeat(mean_offset, N),
        'slope_f2': np.repeat(slope_f2_val, N)
        })
    experiment.from_df(inputs)
    experiment.wait(milliseconds=1000)

# run the experiment I (or II)
tag_exp = "experiment_I"
experiment_id_I = experiment.submit(tag=tag_exp)


""" 
Define  experiment III (SPICE-Net noise) 
for estimating the noise of experiment I (or II)
"""


N_3 = 5000 # Total number of measurements for experiment III

inputs_3 = pd.DataFrame({
    'green': np.repeat(0, N_3),
    'sps_current_ls': np.repeat(sps_current_ls_val, N_3),
    'offset_current_ls': np.repeat(mean_offset, N_3),
    'slope_f2': np.repeat(slope_f2_val, N_3)
})

# run experiment III
experiment_3 = rlab.new_experiment(chamber_id = 'your_chamber_id', config ='linked_leds')
experiment_3.from_df(inputs_3)

tag_exp_3 = "experiment_III"
experiment_id_III = experiment_3.submit(tag=tag_exp_3)


""" 
Results of the experiments
"""


# check the results
_ = rlab.get_experiments(print_max=15)

# download data
reference_df = rlab.download_data(experiment_id_I, root='store_your_data').dataframe
