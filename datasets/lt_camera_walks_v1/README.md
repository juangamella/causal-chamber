# Dataset: lt\_camera\_walks\_v1

[<<< Back to all datasets](https://github.com/juangamella/causal-chamber)

If you use any of the datasets or source code in your work, please consider citing:

```
﻿@article{gamella2025chamber,
  author={Gamella, Juan L. and Peters, Jonas and B{\"u}hlmann, Peter},
  title={Causal chambers as a real-world physical testbed for {AI} methodology},
  journal={Nature Machine Intelligence},
  doi={10.1038/s42256-024-00964-x},
  year={2025},
}
```

## Download

| Link     | MD5 Checksum                     |
|:--------:|:--------------------------------:|
| [ZIP file](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/lt_camera_walks_v1.zip) | 097f291680a9a57d2c62bd2bc2b78fce |

You can also import the dataset directly into your Python code with the [`causalchamber`](https://github.com/juangamella/causal-chamber-package) package. Install it using pip, e.g.

```
pip install causalchamber
```

Then, load the data from any experiment as follows.

```python
from causalchamber.datasets import Dataset

# Download the dataset and store it, e.g., in the current directory
dataset = Dataset('lt_camera_walks_v1', root='./', download=True)

# Load the observations and images from an experiment (see experiment names below)
experiment = dataset.get_experiment(name='actuator_mix')
observations = experiment.as_pandas_dataframe()
images = experiment.as_image_array(size='50')
```

See the table [below](#dataset-description) for all the available experiments and their names.

You can check at which sizes (in pixels) the images are available with

```python
experiment.available_sizes()

# Output:
# ['full', '500', '200']
```
where `full` corresponds to `2000x2000` pixels.

## Dataset Description

| Chamber      | Configuration |
|:------------:|:-------------:|
| Light tunnel | camera        |

This dataset contains experiments where the manipulable variables are set according to different time series. After each step, a measurement is collected from the chamber, including an image taken by the camera.

The file [variables.csv](variables.csv) contains a brief description of each variable (column) in the `.csv` files; see appendix II of the [manuscript](https://arxiv.org/pdf/2404.11341.pdf) for more details. The table below describes the experiments in the dataset. For a precise description of each experiment protocol, see the corresponding Python script used to generate it.

| Experiment | Generator | Description |
|:----------------------:|:---------:|:------------|
|   actuator\_mix  |    [`generators/actuator_mix.py`](generators/actuator_mix.py) | We vary the value of $R,G,B, \theta_1, \theta_2$ following a sine, sawtooth, chirp, triangular and square signal, respectively (see [`scipy.signal`](https://docs.scipy.org/doc/scipy/reference/signal.html#waveforms)). We collect a total of $N=10^4%$ observations. Used in task d3 of the ICA case study (Fig. 6 of the original [paper](https://arxiv.org/pdf/2404.11341.pdf)). |
|   color\_mix  |    [`generators/color_mix.py`](generators/color_mix.py) | We vary the value of $R,G,B$ following a sine, square, and sawtooth wave, respectively. We collect a total of $N=10^4%$ observations. |
|   ar\_1\_uniform\_ref | [`generators/actuators_ar.py`](generators/actuators_ar.py) | We sample the values of $R,G,B,\theta_1,\theta_2$ from scaled and shifted stationary $\text{AR}(1)$. For each actuator, we sample $N=3\times10^{4}$ observations from the $\text{AR}(1)$ process $X(t) := \varphi X(t-1) + \epsilon_t$ where $\epsilon_1,\ldots,\epsilon_N \overset{\text{i.i.d.}}{\sim} \text{Unif}[-1,1]$ and $\varphi = 0.5, 0.6, 0.7, 0.8, 0.9$ for $R,G,B,\theta_1$ and $\theta_2$, respectively. For each actuator, we then shift and scale $X(t)$ so that its values fall in the range $[\mu - \Delta, \mu + \Delta]$, where $(\mu,\Delta) := (128,120)$ for $R,G,B$ and $(\mu,\Delta) := (0,20)$ for $\theta_1, \theta_2$. A visualization of the resulting time-series are shown below. |
| ar\_1\_uniform\_pol\_1\_90 | [`generators/actuators_ar.py`](generators/actuators_ar.py) | We repeat the ar\_1\_uniform\_ref experiment above, but we set $\mu := 90$ for $\theta_1$, effectively shifting the mean of its stochastic process by 90 (degrees). |
| ar\_1\_uniform\_pol\_12\_30 | [`generators/actuators_ar.py`](generators/actuators_ar.py) | We repeat the ar\_1\_uniform\_ref experiment above, but we set $\mu := 30$ for $\theta_1$ and $\theta_2$, effectively shifting the mean of their stochastic processes by 30 (degrees). |

## Visualization

Below we plot the actuator time-series for the _ar\_1\_uniform\*_ experiments.

![](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/actuators_ar_1_uniform_ref.png?)
![](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/actuators_ar_1_uniform_pol_1_90.png?)
![](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/actuators_ar_1_uniform_pol_12_30.png?)

## Changelog

| Dataset version | Date       | Description                                             |
|:---------------:|:----------:|:-------------------------------------------------------:|
| v1.0            | 26.03.2024 | Initial release of the dataset.                         |
| v1.1            | 08.10.2024 | Added the _ar\_1\_uniform\_ref_ experiment.             |
| v1.2            | 09.10.2024 | Added the _ar\_1\_uniform\_ref\_pol\_1\_90_ experiment. |


## Compiling the Experiment Protocols

You can generate the experiment protocols by running `make protocols` in a make-capable machine. This will execute the Python scripts in `generators/` and store the resulting protocols in `protocols/`. The file [`generators/requirements.txt`](generators/requirements.txt) contains the dependencies needed to run the scripts.


## Licenses

We use different licenses for the datasets and software.

### Dataset License

All images and `.csv` files in the dataset are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_DATASETS.txt](LICENSE_DATASETS.txt).

### Software License

All other software, including but not limited to Makefiles and Python scripts, are licensed under the [MIT license](https://opensource.org/license/mit/). A copy of the license can be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).

