# Dataset: lt\_color\_regression\_v1

[<<< Back to all datasets](https://github.com/juangamella/causal-chamber)

If you use any of the datasets or source code in your work, please consider citing:

```
@article{gamella2024chamber,
  title={The Causal Chambers: Real Physical Systems as a Testbed for AI Methodology},
  author={Gamella, Juan L. and B\"uhlmann, Peter and Peters, Jonas},
  journal={arXiv preprint arXiv:2404.11341},
  year={2024}
}
```

## Download

| Link     | MD5 Checksum                     |
|:--------:|:--------------------------------:|
| [ZIP file](TEMPLATE) | 8e2742277e7ad978301eb830148e1d40 |

You can also import the dataset directly into your Python code with the [`causalchamber`](https://pypi.org/project/causalchamber/) package. Install it using pip, e.g.

```
pip install causalchamber
```

Then, load the data from any experiment as follows.

```python
from causalchamber.datasets import Dataset

# Download the dataset and store it, e.g., in the current directory
dataset = Dataset('lt_color_regression_v1', root='./', download=True)

# Load the observations and images from an experiment (see experiment names below)
experiment = dataset.get_experiment(name='bright_colors')
observations = experiment.as_pandas_dataframe()
images = experiment.as_image_array(size='100')
```

See the table [below](#dataset-description) for all the available experiments and their names.

You can check at which sizes (in pixels) the images are available with

```python
experiment.available_sizes()

# Output:
# ['100', '500']
```

## Dataset Description

| Chamber      | Configuration |
|:------------:|:-------------:|
| Light tunnel | camera        |

The dataset consists of experiments where the color of the light source ($R,G,B$) is set at random before taking each image, while the polarizer angles and camera parameters are kept constant. The different experiments correspond to variations in the values of the polarizer angles and camera parameters, or the range from which the values for $R,G,B$ are sampled (see the *brighter\_colors* experiment below). The dataset is used for task b2 (Fig. 5) of the original [manuscript](https://arxiv.org/pdf/2404.11341.pdf).

The file [variables.csv](variables.csv) contains a brief description of each variable (column) in the `.csv` files; see appendix II of the [manuscript](https://arxiv.org/pdf/2404.11341.pdf) for more details. The table below describes the experiments in the dataset. For a precise description of each experiment protocol, see the corresponding Python script used to generate it.

| Experiment | Generator | Description |
|:----------------------:|:---------:|:------------|
| v1.0            | TEMPLATE | Initial release of the dataset. |

## Changelog

| Dataset version | Date       | Description                     |
|:---------------:|:----------:|:-------------------------------:|
| reference | [`generators/color_regression.py`](generators/color_regression.py) | We set $\theta_1=\theta_2=0$, $\text{Ap}=1.8$, $\text{ISO}=100$, $T_\text{Im}=1/200$. Then, we sample $R, G, B \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{0,\ldots,128\\})$ and take an image, repeating the process for a total of $N=10000$ observations. |
| bright_colors | [`generators/color_regression.py`](generators/color_regression.py) | Same as the reference experiment, but we sample $R, G, B \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{129,\ldots,255\\})$ |
| pol_1_45 | [`generators/color_regression.py`](generators/color_regression.py) | Same as the reference experiment, but we set $\theta_1 = 45$. |
| pol_1_90 | [`generators/color_regression.py`](generators/color_regression.py) | Same as the reference experiment, but we set $\theta_1 = 90$. |
| aperture_5.0 | [`generators/color_regression.py`](generators/color_regression.py) | Same as the reference experiment, but we set $\text{Ap}=5$. |
| aperture_11.0 | [`generators/color_regression.py`](generators/color_regression.py) | Same as the reference experiment, but we set $\text{Ap}=11$. |
| shutter_speed_0.002 | [`generators/color_regression.py`](generators/color_regression.py) | Same as the reference experiment, but we set $T_\text{Im}=1/500$. |
| shutter_speed_0.001 | [`generators/color_regression.py`](generators/color_regression.py) | Same as the reference experiment, but we set $T_\text{Im}=1/100$. |
| iso_500.0 | [`generators/color_regression.py`](generators/color_regression.py) | Same as the reference experiment, but we set $\text{ISO}=500$. |
| iso_1000.0 | [`generators/color_regression.py`](generators/color_regression.py) | Same as the reference experiment, but we set $\text{ISO}=1000$. |

## Compiling the Experiment Protocols

You can generate the experiment protocols by running `make protocols` in a make-capable machine. This will execute the Python scripts in `generators/` and store the resulting protocols in `protocols/`. The file [`generators/requirements.txt`](generators/requirements.txt) contains the dependencies needed to run the scripts.


## Licenses

We use different licenses for the datasets and software.

### Dataset License

All images and `.csv` files in the dataset are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_DATASETS.txt](LICENSE_DATASETS.txt).

### Software License

All other software, including but not limited to Makefiles and Python scripts, are licensed under the [MIT license](https://opensource.org/license/mit/). A copy of the license can be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).

