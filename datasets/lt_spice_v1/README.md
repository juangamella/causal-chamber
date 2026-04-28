# Dataset: lt\_crl\_benchmark\_v1

[<<< Back to all datasets](https://github.com/juangamella/causal-chamber)

If you use any of the datasets or source code in your work, please consider citing:

```
@article{vollmer2026identifying,
  title={Identifying Causal Effects Using a Single Proxy Variable},
  author={Vollmer, Silvan and Pfister, Niklas and Weichwald, Sebastian},
  journal={arXiv preprint arXiv:2604.09135},
  year={2026}
}
```

and

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
| [ZIP file](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/lt_crl_benchmark_v1.zip) | 8ec492afffd0142abd70b1fa7082b104 |

You can also import the dataset directly into your Python code with the [`causalchamber`](https://github.com/juangamella/causal-chamber-package) package. Install it using pip, e.g.

```
pip install causalchamber
```

Then, load the data from any experiment as follows.

```python
from causalchamber.datasets import Dataset

# Download the dataset and store it, e.g., in the current directory
dataset = Dataset('lt_spice_v1', root='./', download=True)

# Load the observations from an experiment (see experiment names below)
experiment = dataset.get_experiment(name='exp_1_low_noise')
observations = experiment.as_pandas_dataframe()
```

See the table [below](#dataset-description) for all the available experiments and their names.

## Dataset Description

| Chamber      | Configuration |
|:------------:|:-------------:|
| [Light Tunnel Mk2](https://docs.causalchamber.ai/the-chambers/light-tunnel-mk2) | [linked\_leds](https://cchamber-box.s3.eu-central-2.amazonaws.com/config_doc_lt_mk2_linked_leds.pdf) |

This dataset contains the experimental data used in the 2026 paper ["*Identifying Causal Effects Using a Single Proxy Variable*"](https://arxiv.org/pdf/2604.09135) by Silvan Vollmer, Niklas Pfister and Sebastian Weichwald. The paper studies the problem of causal effect estimation when the confounder can only be indirectly observed through a noisy measurement (proxy). The authors use the [Light Tunnel Mk2](https://docs.causalchamber.ai/the-chambers/light-tunnel-mk2) from Causal Chamber® to evaluate their method on a real, physical system matching this setting. The setup, including the used chamber inputs, is shown in the figure below.

![The chamber setup for the paper.](https://cchamber-box.s3.eu-central-2.amazonaws.com/figure_setup.png)

See the [documentation](https://cchamber-box.s3.eu-central-2.amazonaws.com/config_doc_lt_mk2_linked_leds.pdf) of the linked\_leds configuration for a detailed description of all variables and the causal ground-truth graph of the physical system. The table below describes the experiments in the dataset.

| Experiment             | Generator                                    | Description |
|:----------------------:|:--------------------------------------------:|:------------|
| exp\_1\_low\_noise | [`generators/spice.py`](generators/spice.py) | Data for Experiment I (Low Noise) used in Vollmer et al. (2026, [Figure 4](https://arxiv.org/pdf/2604.09135#page=14.21)). The sampling procedure for the chamber parameters (marked I/P in the figure above) are given in Vollmer et al. (2026, [Table 6](https://arxiv.org/pdf/2604.09135#page=44)). |
| exp\_2\_noisy | [`generators/spice.py`](generators/spice.py) | Data for Experiment II (Noisy) used in Vollmer et al. (2026, [Figure 4](https://arxiv.org/pdf/2604.09135#page=14.21)). The sampling procedure for the chamber parameters (marked I/P in the figure above) are given in Vollmer et al. (2026, [Table 6](https://arxiv.org/pdf/2604.09135#page=44)). |            |
| exp\_3\_spice\_net\_noise\_1 | [`generators/spice.py`](generators/spice.py) | Data for experiment III-1 (SPICE-Net Noise) used to estimate the ground-truth noise distribution in the setting of Experiment I. The sampling procedure for the chamber parameters (marked I/P in the figure above) are given in Vollmer et al. (2026, [Table 6](https://arxiv.org/pdf/2604.09135#page=44)).  |
| exp\_3\_spice\_net\_noise\_2 | [`generators/spice.py`](generators/spice.py) | Data for experiment III-2 (SPICE-Net Noise) used to estimate the ground-truth noise distribution in the setting of Experiment II. The sampling procedure for the chamber parameters (marked I/P in the figure above) are given in Vollmer et al. (2026, [Table 6](https://arxiv.org/pdf/2604.09135#page=44)).  |

## Changelog

| Dataset version | Date       | Description                                             |
|:---------------:|:----------:|:-------------------------------------------------------:|
| v1.0            | 28.04.2026 | Initial release of the dataset.                         |

## Replicating the experiments using the [Remote Lab](https://causalchamber.ai?utm_source=spicedataset)

You can collect a fresh copy of the datasets from a Causal Chamber® by running the script [`generators/spice.py`](generators/spice.py). To do so, you will need access to the [Remote Lab](https://causalchamber.ai?utm_source=spicedataset). The file [`generators/requirements.txt`](generators/requirements.txt) contains the dependencies needed by the script.

## Licenses

We use different licenses for the datasets and software.

### Dataset License

All images and `.csv` files in the dataset (incl. the figure above) are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_DATASETS.txt](LICENSE_DATASETS.txt).

### Software License

All other software, including but not limited to Makefiles and Python scripts, are licensed under the [MIT license](https://opensource.org/license/mit/). A copy of the license can be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).

