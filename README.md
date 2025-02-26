# The Causal Chambers: Dataset Repository

[![PyPI version](https://badge.fury.io/py/causalchamber.svg)](https://badge.fury.io/py/causalchamber)
[![Downloads](https://static.pepy.tech/badge/causalchamber)](https://pepy.tech/project/causalchamber)
[![License: CC-BY 4.0](https://img.shields.io/static/v1.svg?logo=creativecommons&logoColor=white&label=License&message=CC-BY%204.0&color=yellow)](https://creativecommons.org/licenses/by/4.0/)
[![Donate](https://img.shields.io/static/v1.svg?logo=Github%20Sponsors&label=donate&message=Github%20Sponsors&color=e874ff)](https://github.com/sponsors/juangamella)


![The Causal Chambers: (left) the wind tunnel, and (right) the light tunnel with the front panel removed to show its interior.](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/the_chambers.jpg)

This repository contains datasets collected from the _causal chambers_, the two devices described in the 2025 paper [*Causal chambers as a real-world physical testbed for AI methodology*](https://www.nature.com/articles/s42256-024-00964-x) by Juan L. Gamella, Jonas Peters and Peter Bühlmann. The repository is updated as we collect new datasets from the chambers.

The datasets are publicly available through a permissive [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). This means you are free to use, share and modify the datasets as long as you give appropriate credit and communicate changes. If you use the datasets in your scientific work, please consider citing:

```
﻿@article{gamella2025chamber,
  author={Gamella, Juan L. and Peters, Jonas and B{\"u}hlmann, Peter},
  title={Causal chambers as a real-world physical testbed for {AI} methodology},
  journal={Nature Machine Intelligence},
  doi={10.1038/s42256-024-00964-x},
  year={2025},
}
```

Here you can also find the resources to build the chambers (see [`hardware/`](hardware/)).

The code to reproduce the case studies in the original paper can be found in the separate [paper repository](https://github.com/juangamella/causal-chamber-paper).

See also the [separate repository](https://github.com/juangamella/causal-chamber-package) for the `causalchamber` [package](https://github.com/juangamella/causal-chamber-package), which allows you to directly download datasets to your Python code, load ground-truth graphs, access the remote API, and use the physical simulators of the chambers.

## Need help?

If you need help choosing the right dataset for your work, please write us an [email](mailto:juangamella@gmail.com).

## Available datasets

We are open to suggestions of additional experiments that may prove interesting; please reach out via [email](mailto:juangamella@gmail.com).

Each dataset is described in detail in its corresponding page (click the dataset name), together with the download instructions. The chamber configurations are described in [Fig. 3](https://www.nature.com/articles/s42256-024-00964-x/figures/3) of the [manuscript](https://www.nature.com/articles/s42256-024-00964-x).

| Dataset name | Notes | Chamber | Config. |
|--------:|:--------------------------------|:--------:|:--------:|
| [lt_crl_benchmark_v1](datasets/lt_crl_benchmark_v1/) | Datasets for the 2025 benchmark paper "*Sanity Checking Causal Representation Learning on a Simple Real-World System*" by Juan L. Gamella\*, Simon Bing\*, and Jakob Runge. | Light tunnel | camera |
| [lt_camera_walks_v1](datasets/lt_camera_walks_v1/) | Image data for the ICA case study (task d3, Fig. 6). | Light tunnel | camera |
| [lt_color_regression_v1](datasets/lt_color_regression_v1/) | Image data for task b2 in the OOD case study (Fig. 5) | Light tunnel | camera |
| [lt_interventions_standard_v1](datasets/lt_interventions_standard_v1/) | Observational and interventional data from the light tunnel, used for the causal discovery case study in Fig. 5. | Light tunnel | standard |
| [lt_walks_v1](datasets/lt_walks_v1/) | Random and deterministic walks of the light-tunnel actuators. Used in the ICA case study (task d1), Fig. 6. | Light tunnel | standard |
| [wt_walks_v1](datasets/wt_walks_v1/) | Random and deterministic walks of the wind-tunnel actuators. Used in the causal discovery (task a3) and ICA (task d2) case studies. | Wind tunnel | standard |
| [lt_malus_v1](datasets/lt_malus_v1/) | Measurements of light intensity displaying Malus' law, used in the symbolic regression task in Fig. 6e. | Light tunnel | standard |
| [wt_bernoulli_v1](datasets/wt_bernoulli_v1/) | Measurements of air pressure displaying Bernoulli's principle, used in the symbolic regression task in Fig. 6e. | Wind tunnel | standard |
| [wt_changepoints_v1](datasets/wt_changepoints_v1/) | Used for the change point detection case study in Fig. 5. | Wind tunnel | standard |
| [wt_intake_impulse_v1](datasets/wt_intake_impulse_v1/) | Barometric pressure curves used in task 2c, Fig. 5. | Wind tunnel | standard |
| [wt_pressure_control_v1](datasets/wt_pressure_control_v1/) | Data from the pressure-control configuration of the wind tunnel. | Wind tunnel | pressure-control |
| [lt_test_v1](datasets/lt_test_v1/) | Experiments to characterize some of the physical effects of the light tunnel. Shown in figures 7-15 of the manuscript. | Light tunnel | standard |
| [wt_test_v1](datasets/wt_test_v1/) | Experiments to characterize some of the physical effects of the wind tunnel. Shown in figures 7-15 of the manuscript. | Wind tunnel | standard |
| [lt_camera_test_v1](datasets/lt_camera_test_v1/) | Experiments to characterize some of the physical effects of the camera system in the light tunnel. | Light tunnel | camera |
| [wt_validate_v1](datasets/wt_validate_v1/) | Randomized control experiments to validate the causal ground-truth graph of the wind tunnel in its _standard_ configuration (appendix V of the manuscript). | Wind tunnel | standard |
| [wt_pc_validate_v1](datasets/wt_pc_validate_v1/) | Randomized control experiments to validate the causal ground-truth graph of the wind tunnel in its _pressure-control_ configuration (appendix V of the manuscript). | Wind tunnel | pressure-control |
| [lt_validate_v1](datasets/lt_validate_v1/) | Randomized control experiments to validate the causal ground-truth graphs of the light tunnel in its _standard_ configuration (appendix V of the manuscript). | Light tunnel | standard |
| [lt_camera_validate_v1](datasets/lt_camera_validate_v1/) | Randomized control experiments to validate the causal ground-truth graphs of the light tunnel in its _camera_ configuration (appendix V of the manuscript). | Light tunnel | standard |
| [lt_camera_v1](datasets/lt_camera_v1/) | Image datasets where the light-tunnel actuators are sampled from different distributions and structural causal models. | Light tunnel | camera |

## Downloading the datasets

If you use Python, you can directly import a dataset into your code through the `causalchamber` [package](https://github.com/juangamella/causal-chamber-package). For example, you can load the [`lt_camera_test_v1`](https://github.com/juangamella/causal-chamber/tree/main/datasets/lt_camera_test_v1) image dataset as follows:

```python
import causalchamber.datasets as datasets

# Download the dataset and store it, e.g., in the current directory
dataset = datasets.Dataset(name='lt_camera_test_v1', root='./', download=True)

# Select an experiment and load the observations and images
experiment = dataset.get_experiment(name='palette')

observations = experiment.as_pandas_dataframe()
images = experiment.as_image_array(size='200')
```

See each dataset page for a tailored example (e.g., [here](datasets/lt_test_v1/)), and the package [repository](https://github.com/juangamella/causal-chamber-package) for more details & documentation.

You can also download a `.zip` file with all the data, including the images at different resolutions. The link and checksum (to verify integrity) are available on the dataset pages (click on the dataset name in the table above).

## Licenses

All images and `.csv` files in the datasets are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE.txt](LICENSE.txt).

## Contributing

If you would like to make a (highly welcome!) contribution towards the costs of running this repository, you can do so as a [Github sponsor](https://github.com/sponsors/juangamella).

