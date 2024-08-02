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
| [ZIP file](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/lt_camera_v1.zip) | c0a65e8fa6b8d53ace03c6227da79528 |

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
experiment = dataset.get_experiment(name='uniform_ap_1.8_iso_500.0_ss_0.005')
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
| Light tunnel | camera        |

The repository contains experiments where the chamber actuators $R,G,B,\theta_1,\theta_2$ are set following different distributions and an image is taken for each setting. Some experiments are repeated under different configurations of the camera parameters (aperture, sensor gain and shutter speed).

The file [variables.csv](variables.csv) contains a brief description of each variable (column) in the `.csv` files; see appendix II of the [manuscript](https://arxiv.org/pdf/2404.11341.pdf) for more details. The table below describes the experiments in the dataset. For a precise description of each experiment protocol, see the corresponding Python script used to generate it.

| Experiment | Generator | Description |
|:----------------------:|:---------:|:------------|
| uniform\_ap\_1.8\_iso\_500.0\_ss\_0.005<br>uniform\_ap\_1.8\_iso\_1000.0\_ss\_0.005<br>uniform\_ap\_1.8\_iso\_500.0\_ss\_0.001<br>uniform\_ap\_8.0\_iso\_500.0\_ss\_0.005 | [`generators/random_actuators.py`](generators/random_actuators.py)| We set the camera parameters ($\text{Ap}, \text{ISO}, T_\text{Im}$) to the values given in the experiment name (ap, iso, ss, respectively). Then, for a total of $N=10^4$ times, we sample $R,G,B \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{0,\ldots,255\\})$, $\theta_1, \theta_2 \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{-180,-179.9,\ldots,180\\})$, and take a measurement, producing an image. |
| betab\_ap\_1.8\_iso\_500.0\_ss\_0.005 | [`generators/betabinom.py`](generators/betabinom.py)| We set the camera parameters $\text{Ap}=1.8, \text{ISO}=500, T_\text{Im}=1/200$). Then, for a total of $N=10^4$ times, we sample the actuators independently from a BetaBinomial distribution, i.e. $R,G,B \overset{\text{i.i.d.}}{\sim} \text{BetaBin}(n=255,\alpha=\beta=5)$, $\theta_1, \theta_2 \overset{\text{i.i.d.}}{\sim} \text{BetaBin}(n=180,\alpha=\beta=5) - 180$, and take a measurement, producing an image. The resulting histograms of the actuator values are shown below.|

| scm\_1\_reference | [`generators/scms.py`](generators/scms.py)| The camera parameters are fixed to $\text{Ap} = 1.8, \text{ISO} = 500, T_\text{Im}=0.005$ and we collect $N=5000$ observations as follows. We sample $Z := (R, G, B, \theta_1, \theta_2)^T$ following a linear structural causal model, given by $Z := S\tilde{Z} + l$ with $S := \mathrm{diag}(255, 255, 255, 180, 180)$, $l:=(0,0,0,-90,-90)^T$ and $$\tilde{Z} = W\tilde{Z} + D\epsilon,$$ where the non-zero elements of $W$ correspond to a DAG adjacency, $D$ is a diagonal matrix with positive entries, and $\epsilon \in \mathbb{R}^5$ is a random vector with mutually independent components $\epsilon_i \overset{\text{i.i.d.}}{\sim} \mathrm{Unif}[0,1]$. We sample the non-zero entries of $W$ and $D$ uniformly and independently at random from $[0,1]$, and then scale the rows so they sum to one. The entries of $W$ and $D$ are given in [`scm_1.py`](scm_1.py).|
| scm\_1\_red<br>scm\_1\_green<br>scm\_1\_blue<br>scm\_1\_pol_1<br>scm\_1\_pol_2 | [`generators/scms.py`](generators/scms.py)| For each experiment *scm\_1\_\<target\>*, we sample the actuators $Z := (R, G, B, \theta_1, \theta_2)^T$ from the same SCM as in *scm\_1\_reference*, but under a perfect intervention on variable \<target\>. For a target with index $i$, the intervention consists of removing the effect of its parents, i.e., $W_{ij} \leftarrow 0$ for $j=1,\ldots,5$, and shifting the distribution of the corresponding noise term to $\epsilon_i \overset{\text{i.i.d.}}{\sim} \mathrm{Unif}[0.75,1]$. We collect $N=5000$ observations for each experiment.|

## Visualization

Below we plot the actuator distributions for the _betab\_ap\_1.8\_iso\_500.0\_ss\_0.005_ experiment.

![](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/actuators_betabinomials.png)

## Changelog

| Dataset version | Date       | Description                     |
|:---------------:|:----------:|:-------------------------------:|
| v1.0            | 27.06.2024 | Initial release of the dataset. |

## Compiling the Experiment Protocols

You can generate the experiment protocols by running `make protocols` in a make-capable machine. This will execute the Python scripts in `generators/` and store the resulting protocols in `protocols/`. The file [`generators/requirements.txt`](generators/requirements.txt) contains the dependencies needed to run the scripts.


## Licenses

We use different licenses for the datasets and software.

### Dataset License

All images and `.csv` files in the dataset are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_DATASETS.txt](LICENSE_DATASETS.txt).

### Software License

All other software, including but not limited to Makefiles and Python scripts, are licensed under the [MIT license](https://opensource.org/license/mit/). A copy of the license can be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).

