# Dataset: lt\_camera\_test\_v1

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
| [ZIP file](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/lt_camera_test_v1.zip) | f31537ce8db74c537ab2f9ffa2f6f1f9 |

You can also import the dataset directly into your Python code with the [`causalchamber`](https://pypi.org/project/causalchamber/) package. Install it using pip, e.g.

```
pip install causalchamber
```

Then, load the data from any experiment as follows.

```python
from causalchamber.datasets import Dataset

# Download the dataset and store it, e.g., in the current directory
dataset = Dataset('lt_camera_test_v1', root='./', download=True)

# Load the observations and images from an experiment (see experiment names below)
experiment = dataset.get_experiment(name='palette')
observations = experiment.as_pandas_dataframe()
images = experiment.as_image_array(size='200')
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

The repository contains experiments to test the effect of different actuators and camera parameters on the captured images.

The file [variables.csv](variables.csv) contains a brief description of each variable (column) in the `.csv` files; see appendix II of the [manuscript](https://arxiv.org/pdf/2404.11341.pdf) for more details. The table below describes the experiments in the dataset. For a precise description of each experiment protocol, see the corresponding Python script used to generate it.

| Experiment | Generator | Description |
|:----------------------:|:---------:|:------------|
| palette      | [`generators/palette.py`](generators/palette.py) | Capture images of 14 different light-source colors ($R,G,B$) for combinations of the camera parameters $(\text{Ap}, \text{ISO}, T_\text{Im}) \in \\{1.8, 11\\} \times \\{100,1000\\} \times \\{0.005, 0.001\\}.$ |
| polarizer\_effect\_bright<br>polarizer\_effect\_dark      | [`generators/polarizer_effect.py`](generators/polarizer_effect.py) | Capture images of primary light-source colors and their combinations under different positions of the polarizers, in a high-exposure setting (bright, $\text{Ap}=1.8, \text{ISO}=1000, T_\text{Im}=0.005$) and a low-exposure setting (dark, $\text{Ap}=22, \text{ISO}=100, T_\text{Im}=0.001$).|
| pure\_colors\_bright<br>pure\_colors\_dark      | [`generators/pure_colors.py`](generators/pure_colors.py) | Capture images of pure red $(R=255, G=B=0)$, green $(R=B=0, G=255)$ and blue $(R=G=0, B=255)$ under aligned polarizers, in a high-exposure setting (bright, $\text{Ap}=1.8, \text{ISO}=1000, T_\text{Im}=0.005$) and a low-exposure setting (dark, $\text{Ap}=22, \text{ISO}=100, T_\text{Im}=0.001$).|
| aperture | [`generators/parameters.py`](generators/parameters.py) | We iterate over all possible values of $\text{Ap}$  while keeping the other parameters fixed at $\text{ISO}=100$ and $T_\text{Im}=1/200$. For each value of $\text{Ap}$, we take an image for different intensities of white, red, green and blue light from the light source. |
| iso | [`generators/parameters.py`](generators/parameters.py) | We iterate over all possible values of $\text{ISO}$  while keeping the other parameters fixed at $\text{Ap}=1.8$ and $T_\text{Im}=1/200$. For each value of $\text{ISO}$, we take an image for different intensities of white, red, green and blue light from the light source. |
| shutter\_speed | [`generators/parameters.py`](generators/parameters.py) | We iterate over all possible values of $T_\text{Im}$ while keeping the other parameters fixed at $\text{Ap}=1.8$ and $\text{ISO}=100$. For each value of $T_\text{Im}$, we take an image for different intensities of white, red, green and blue light from the light source. |

## Changelog

| Dataset version | Date       | Description                     |
|:---------------:|:----------:|:-------------------------------:|
| v1.0            | 24.03.2024 | Initial release of the dataset. 
| v1.1            | 20.09.2024 | Added aperture, iso and shutter\_speed experiments. |

## Compiling the Experiment Protocols

You can generate the experiment protocols by running `make protocols` in a make-capable machine. This will execute the Python scripts in `generators/` and store the resulting protocols in `protocols/`. The file [`generators/requirements.txt`](generators/requirements.txt) contains the dependencies needed to run the scripts.


## Licenses

We use different licenses for the datasets and software.

### Dataset License

All images and `.csv` files in the dataset are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_DATASETS.txt](LICENSE_DATASETS.txt).

### Software License

All other software, including but not limited to Makefiles and Python scripts, are licensed under the [MIT license](https://opensource.org/license/mit/). A copy of the license can be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).

