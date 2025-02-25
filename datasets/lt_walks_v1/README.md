# Dataset: lt\_walks\_v1

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
| [ZIP file](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/lt_walks_v1.zip) | dcad019186661a56de7a2d1db97fc2f0 |

You can also import the dataset directly into your Python code with the [`causalchamber`](https://pypi.org/project/causalchamber/) package. Install it using pip, e.g.

```
pip install causalchamber
```

Then, load the data from any experiment as follows.

```python
from causalchamber.datasets import Dataset

# Download the dataset and store it, e.g., in the current directory
dataset = Dataset('lt_walks_v1', root='./', download=True)

# Load the data from an experiment (see experiment names below)
experiment = dataset.get_experiment(name='color_mix')
df = experiment.as_pandas_dataframe()
```

See the table [below](#dataset-description) for all the available experiments and their names.

## Dataset Description

| Chamber      | Configuration |
|:------------:|:-------------:|
| Light tunnel | standard      |


The dataset contains experiments where the manipulable variables of the light tunnel are set according to different time series: either deterministic (e.g., sinusoid, sawtooth or square waves in the `color_mix` experiment) or stochastic, e.g., white noise or following a random walk. After each step, a measurement is collected from the chamber.

The file [variables.csv](variables.csv) contains a brief description of each variable (column) in the `.csv` files; see appendix II of the [manuscript](https://arxiv.org/pdf/2404.11341.pdf) for more details. The table below describes the experiments in the dataset. For a precise description of each experiment protocol, see the corresponding Python script used to generate it.

| Experiment | Generator | Description |
|:----------------------:|:---------:|:------------|
| actuators\_white| [`generators/actuators_white.py`](generators/actuators_white.py)| The values of all actuators are sampled uniformly at random before each measurement, i.e., $R,G,B,L_{11},\ldots,L_{32} \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{0,\ldots,255\\})$ and $\theta_1, \theta_2 \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{-90,-89,\ldots,90\\})$. | 
|   color\_mix  |    [`generators/color_mix.py`](generators/color_mix.py) | We vary the value of $R,G,B$ according to a sine, square and sawtooth wave, respectively. We collect a total of $N=10^4%$ observations. The dataset is used in task d1 of the ICA case study (see [Fig. 6](https://arxiv.org/pdf/2404.11341.pdf)). |
|   smooth\_polarizers  |    [`generators/smooth_polarizers.py`](generators/smooth_polarizers.py) | The tunnel inputs $R,G,B,L\_{31},L\_{32}$ are sampled from the stochastic process shown below, i.e., each is sampled independently from a uniform distribution, with block changes in variance and mean. The first polarizer ($\theta\_1$) slowly increases in the range ($-90,180$) while the second polarizer is fixed at $\theta\_2=0$. We collect a total of $n=10000$ observations. |


## Visualization

Below we show the stochastic process of the tunnel inputs in the smooth\_polarizers experiment.

![](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/smooth_polarizers.png)

## Changelog

| Dataset version | Date       | Description                             |
|:---------------:|:----------:|:---------------------------------------:|
| v1.0            | 14.04.2024 | Initial release of the dataset.         |
| v1.1            | 25.02.2025 | Added the smooth\_polarizers experiment |

## Compiling the Experiment Protocols

You can generate the experiment protocols by running `make protocols` in a make-capable machine. This will execute the Python scripts in `generators/` and store the resulting protocols in `protocols/`. The file [`generators/requirements.txt`](generators/requirements.txt) contains the dependencies needed to run the scripts.


## Licenses

We use different licenses for the datasets and software.

### Dataset License

All images and `.csv` files in the dataset are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_DATASETS.txt](LICENSE_DATASETS.txt).

### Software License

All other software, including but not limited to Makefiles and Python scripts, are licensed under the [MIT license](https://opensource.org/license/mit/). A copy of the license can be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).

