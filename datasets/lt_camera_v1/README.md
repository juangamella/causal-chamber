# Dataset: lt\_camera\_v1

[<<< Back to all datasets](http://causalchamber.org)

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
| [ZIP file](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/lt_camera_v1.zip) | TODO |

You can also import the dataset directly into your Python code with the [`causalchamber`](https://pypi.org/project/causalchamber/) package. Install it using pip, e.g.

```
pip install causalchamber
```

Then, load the data from any experiment as follows.

```python
from causalchamber.datasets import Dataset

# Download the dataset and store it, e.g., in the current directory
dataset = Dataset('lt_camera_v1', root='./', download=True)

# Load the observations and images from an experiment (see experiment names below)
experiment = dataset.get_experiment(name='ap_1.8_iso_500.0_ss_0.005')
observations = experiment.as_pandas_dataframe()
images = experiment.as_image_array(size='100')
```

See the table [below](#dataset-description) for all the available experiments and their names.

You can check at which sizes (in pixels) the images are available with

```python
experiment.available_sizes()

# Output:
# ['100']
```


## Dataset Description

| Chamber      | Configuration |
|:------------:|:-------------:|
| Light tunnel | camera |

The repository contains experiments where the chamber actuators $R,G,B,\theta_1,\theta_2$ are set following different distributions and an image is taken for each setting. Some experiments are repeated under different configurations of the camera parameters (aperture, sensor gain and shutter speed).

The file [variables.csv](variables.csv) contains a brief description of each variable (column) in the `.csv` files; see appendix II of the [manuscript](https://arxiv.org/pdf/2404.11341.pdf) for more details. The table below describes the experiments in the dataset. For a precise description of each experiment protocol, see the corresponding Python script used to generate it.

| Experiment | Generator | Description |
|:----------------------:|:---------:|:------------|
| uniform\_ap\_1.8\_iso\_500.0\_ss\_0.005<br>uniform\_ap\_1.8\_iso\_1000.0\_ss\_0.005<br>uniform\_ap\_1.8\_iso\_500.0\_ss\_0.001<br>uniform\_ap\_8.0\_iso\_500.0\_ss\_0.005 | [`generators/random_actuators.py`](lt_camera_v1/generators/random_actuators.py)| We set the camera parameters ($\text{Ap}, \text{ISO}, T_\text{Im}$) to the values given in the experiment name (ap, iso, ss, respectively). Then, for a total of $N=10^4$ times, we sample $R,G,B \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{0,\ldots,255\\})$ and $\theta_1, \theta_2 \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{-180,-179.9,\ldots,180\\})$, and take a measurement, producing an image. |
| scm_1_reference | [`generators/scms.py`](lt_camera_v1/generators/scms.py)| We set the camera parameters to $\text{Ap} = 1.8, \text{ISO} = 500, T_\text{Im}=0.005$ and sample $Z := (R, G, B, \theta_1, \theta_2)^T$ following a structural causal model, given by $Z := S\tilde{Z} + l \epsilon$ where $S := $ and $$\begin{pmatrix}
1 & 2 & 3\\
a & b & c
\end{pmatrix}$$  |


## Changelog

| Dataset version | Date       | Description                     |
|:---------------:|:----------:|:-------------------------------:|
| v1.0            | TODO | Initial release of the dataset. |

## Compiling the Experiment Protocols

You can generate the experiment protocols by running `make protocols` in a make-capable machine. This will execute the Python scripts in `generators/` and store the resulting protocols in `protocols/`. The file [`generators/requirements.txt`](generators/requirements.txt) contains the dependencies needed to run the scripts.


## Licenses

We use different licenses for the datasets and software.

### Dataset License

All images and `.csv` files in the dataset are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_DATASETS.txt](LICENSE_DATASETS.txt).

### Software License

All other software, including but not limited to Makefiles and Python scripts, are licensed under the [MIT license](https://opensource.org/license/mit/). A copy of the license can be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).

