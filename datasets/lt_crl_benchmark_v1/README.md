# Dataset: lt\_crl\_benchmark\_v1

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

and

```
@InProceedings{gamellabing2025sanity,
  title =	 {Sanity Checking Causal Representation Learning on a
                  Simple Real-World System},
  author =	 {Gamella*, Juan L. and Bing*, Simon and Runge, Jakob},
  booktitle =	 {Proceedings of the 42nd International Conference on
                  Machine Learning},
  pages =	 {18143--18169},
  year =	 2025,
  editor =	 {Singh, Aarti and Fazel, Maryam and Hsu, Daniel and
                  Lacoste-Julien, Simon and Berkenkamp, Felix and
                  Maharaj, Tegan and Wagstaff, Kiri and Zhu, Jerry},
  volume =	 267,
  series =	 {Proceedings of Machine Learning Research},
  month =	 {13--19 Jul},
  publisher =	 {PMLR},
  url =		 {https://proceedings.mlr.press/v267/gamella25a.html},
  note =	 {*equal contribution}
}
```


## Download

| Link     | MD5 Checksum                     |
|:--------:|:--------------------------------:|
| [ZIP file](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/lt_crl_benchmark_v1.zip) | 8ec492afffd0142abd70b1fa7082b104 |

You can also import the dataset directly into your Python code with the [`causalchamber`](https://github.com/juangamella/causal-chamber-package) package. Install it using pip, e.g.

```
pip install causalchamber
```

Then, load the data from any experiment as follows.

```python
from causalchamber.datasets import Dataset

# Download the dataset and store it, e.g., in the current directory
dataset = Dataset('lt_crl_benchmark_v1', root='./', download=True)

# Load the observations and images from an experiment (see experiment names below)
experiment = dataset.get_experiment(name='buchholz_1_obs')
observations = experiment.as_pandas_dataframe()
images = experiment.as_image_array(size='64')
```

See the table [below](#dataset-description) for all the available experiments and their names.

You can check at which sizes (in pixels) the images are available with

```python
experiment.available_sizes()

# Output:
# ['64']
```


## Dataset Description

| Chamber      | Configuration |
|:------------:|:-------------:|
| Light tunnel | camera        |

The dataset contains the benchmark data used in the paper "*Sanity Checking Causal Representation Learning on a Simple Real-World System*" (2025) by Juan L. Gamella\*, Simon Bing\* and Jakob Runge. The data is used to evaluate different causal representation learning algorithms.

In each experiment (see below), the "latent causal factors", i.e., the light-source color ($R,G,B$) and polarizer positions ($\theta\_1, \theta\_2$), are sampled from different processes, and an image and sensor measurements (the observations) are taken for each set of values. Each sampling process is detailed in the table below. For all experiments, the camera parameters (aperture, iso, shutter speed) are fixed at ($\text{Ap} = 1.8, \text{ISO} = 500, T_\text{Im}=0.005$).

The file [variables.csv](variables.csv) contains a brief description of each variable (column) in the `.csv` files; see Appendix II of the original [paper](https://arxiv.org/pdf/2404.11341.pdf) for more details. The table below describes the experiments in the dataset. For a precise description of each experiment protocol, see the corresponding Python script used to generate it.

| Experiment | Generator | Description |
|:----------------------:|:---------:|:------------|
| buchholz_1_obs<br>buchholz_1_red<br>buchholz_1_green<br>buchholz_1_blue<br>buchholz_1_pol_1<br>buchholz_1_pol_2 | [`generators/buchholz_1.py`](generators/buchholz_1.py)| The data generation procedure is described in [Appendix A.1.1](https://raw.githubusercontent.com/mlresearch/v267/main/assets/gamella25a/gamella25a.pdf#subsubsection.A.1.1) of the paper. We sample $R,G,B,\theta\_1,\theta\_2$ from  a linear structural causal model (SCM) with additive Gaussian noise; its parameters are given in [params_buchholz_1.py](params_buchholz_1.py). For the observational data (buchholz\_1\_obs),  the independent Gaussian noise variables all have zero mean and a variance sampled from $U([1, 2])$. For the interventional data (buchholz\_1\_red, buchholz\_1\_blue, ...), we consider do-interventions that set their target to a Gaussian $\mathcal{N}(\mu, \sigma^2)$, where $\mu \sim U([1, 2])$ and $\sigma^2 \sim U([-2, -1]) \cup U([1, 2])$. Each variable is intervened upon individually in each environment, and we collect $n = 10000$ samples from each environment (incl. the observational environment). |
| citris_1 | [`generators/citris_1.py`](generators/citris_1.py)| The inputs ($R,G,B,\theta\_1,\theta\_2$) are sampled following the stochastic time-varying process described in [Appendix A.3.1](https://raw.githubusercontent.com/mlresearch/v267/main/assets/gamella25a/gamella25a.pdf#subsubsection.A.3.1) of the paper. We collect a total of $n=100K$ observations from this process. |
| uniform | [`generators/uniform.py`](generators/uniform.py)| The actuators ($R,G,B,\theta\_1,\theta\_2$) are sampled uniformly at random, i.e., $R,G,B \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{0,\ldots,255\\})$, $\theta_1, \theta_2 \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{-90,-89.9,\ldots,90\\})$. We collect a total of $n=2000$ observations. |
| buchholz_1_obs\_synth\_det<br>buchholz_1_red\_synth\_det<br>buchholz_1_green\_synth\_det<br>buchholz_1_blue\_synth\_det<br>buchholz_1_pol_1\_synth\_det<br>buchholz_1_pol_2\_synth\_det<br>citris\_1\_synth\_det<br>uniform\_synth\_det | —| Synthetic equivalents of all the above experiments. The inputs ($R,G,B,\theta\_1,\theta\_2$) are sampled just like in the experiments above, but instead of collecting a real image and measurements from the light tunnel, we generate synthetic equivalents with the simulators described in [Appendix C](https://raw.githubusercontent.com/mlresearch/v267/main/assets/gamella25a/gamella25a.pdf#appendix.C) of the paper. A Python implementation of these simulators—and Jupyter notebooks with tutorials—can be found in the [Simulator Repository](https://github.com/juangamella/causal-chamber-package/tree/main/causalchamber/simulators) of the `causalchamber` [package](https://github.com/juangamella/causal-chamber-package) (see simulators `lt.DecoderSimple` and `lt.Deterministic`. |

## Changelog

| Dataset version | Date       | Description                                             |
|:---------------:|:----------:|:-------------------------------------------------------:|
| v1.0            | 25.02.2024 | Initial release of the dataset.                         |

## Compiling the Experiment Protocols

You can generate the experiment protocols by running `make protocols` in a make-capable machine. This will execute the Python scripts in `generators/` and store the resulting protocols in `protocols/`. The file [`generators/requirements.txt`](generators/requirements.txt) contains the dependencies needed to run the scripts.


## Licenses

We use different licenses for the datasets and software.

### Dataset License

All images and `.csv` files in the dataset are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_DATASETS.txt](LICENSE_DATASETS.txt).

### Software License

All other software, including but not limited to Makefiles and Python scripts, are licensed under the [MIT license](https://opensource.org/license/mit/). A copy of the license can be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).

