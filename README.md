# The Causal Chambers: Dataset Repository

![The Causal Chambers: (left) the wind tunnel, and (right) the light tunnel with the front panel removed to show its interior.](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/the_chambers.jpg)

This repository contains datasets collected from the _causal chambers_, the two devices described in the 2024 paper [*The Causal Chambers: Real Physical Systems as a Testbed for AI Methodology*](https://arxiv.org/pdf/2404.11341.pdf) by Juan L. Gamella, Jonas Peters and Peter Bühlmann. The repository is updated as we collect new datasets from the chambers.

The datasets are publicly available through a permissive [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). This means you are free to use, share and modify the datasets as long as you give appropriate credit and communicate changes. If you use the datasets in your scientific work, please consider citing:

```
@article{gamella2024chamber,
  title={The Causal Chambers: Real Physical Systems as a Testbed for AI Methodology},
  author={Gamella, Juan L. and B\"uhlmann, Peter and Peters, Jonas},
  journal={arXiv preprint arXiv:2404.11341},
  year={2024}
}
```

This repository also contains the source code for the `causalchamber` [package](https://pypi.org/project/causalchamber/) to directly [import the datasets into your Python code](#downloading-the-datasets). The package also provides Python implementations of the [mechanistic models](#mechanistic-models) described in appendix IV of the original [paper](https://arxiv.org/pdf/2404.11341.pdf).

Here you can also find the resources to [build the chambers](#building-the-chambers), and the datasheets for all chamber components (see [`hardware/`](hardware/)).

The code to reproduce the case studies in the original paper can be found in the separate [paper repository](https://github.com/juangamella/causal-chamber-paper).

## Available datasets

We are open to suggestions of additional experiments that may prove interesting; please reach out to the [corresponding author](https://github.com/juangamella).

Each dataset below is described in detail in its corresponding page (click the dataset name). The chamber configurations are described in Fig. 3 of the manuscript.

| Dataset name | Notes | Chamber | Config. |
|--------:|:--------------------------------|:--------:|:--------:|
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

## Downloading the datasets

For each dataset, you can simply download a `.zip` file with all the data, including the images at different resolutions. The link and checksum (to verify integrity) are available on the page of each dataset (click on the dataset name in the table above).

If you use Python, you can directly import a dataset into your code through the `causalchamber` [package](https://pypi.org/project/causalchamber/). You can install it using pip, e.g. by typing

```
pip install causalchamber
```

in an appropriate shell. Datasets can then be accessed directly from your Python code. For example, you can access the light-intensity data for the symbolic regression case study ([Fig. 6e](https://arxiv.org/pdf/2404.11341.pdf)) as follows:

```python
from causalchamber.datasets import Dataset

# Download the dataset and store it, e.g., in the current directory
dataset = Dataset(name='lt_malus_v1', root='./', download=True)

# Select an experiment and load its observations
experiment = dataset.get_experiment(name='white_255')
df = experiment.as_pandas_dataframe()
```

For the available experiment names, see the page for each dataset (click on the dataset name in the table above) or run
```python
dataset.available_experiments()

# Output:
# ['blue_128',
#  'blue_255',
#  'blue_64',
#  'green_128',
#  'green_255',
#  'green_64',
#  'red_128',
#  'red_255',
#  'red_64',
#  'white_128',
#  'white_255',
#  'white_64']
```

## Mechanistic models

The `causalchamber` [package](https://pypi.org/project/causalchamber/) also contains Python implementations of the mechanistic models described in appendix IV of the original [paper](https://arxiv.org/pdf/2404.11341.pdf). The models follow the same nomenclature as in the paper, e.g., to import and run model A1 of the steady-state fan speed:
```Python
import numpy as np
from causalchamber.models import model_a1
model_a1(L=np.linspace(0,1,10), L_min=0.1, omega_max=314.15)

# Output:

# array([ 31.415     ,  34.90555556,  69.81111111, 104.71666667,
#        139.62222222, 174.52777778, 209.43333333, 244.33888889,
#        279.24444444, 314.15      ])
```

The implementations can be found in the [`src/causalchamber/models`](src/causalchamber/models) directory. You can find examples of using the models in the [`case_studies/mechanistic_models.ipynb`](https://github.com/juangamella/causal-chamber-paper/blob/main/case_studies/mechanistic_models.ipynb) notebook in the separate [paper repository](https://github.com/juangamella/causal-chamber-paper).

## Causal ground-truth graphs

The graphs for the causal ground truths given in Fig. 3 of the original [paper](https://arxiv.org/pdf/2404.11341.pdf) can be found as adjacency matrices in  the [`ground_truths/`](ground_truths/) directory. The adjacencies can also be loaded through the `causalchamber` [package](https://pypi.org/project/causalchamber/), e.g., 
```python
from causalchamber.ground_truth import graph
graph(chamber="lt", configuration="standard")

# Output:

#              red  green  blue  osr_c  v_c  current  pol_1  pol_2  osr_angle_1  \
# red            0      0     0      0    0        1      0      0            0   
# green          0      0     0      0    0        1      0      0            0   
# blue           0      0     0      0    0        1      0      0            0   
# osr_c          0      0     0      0    0        1      0      0            0   
```

To make it easier to plot graphs and reference them back to the original paper, the latex representation of each variable can be obtained by calling the `latex_name` function. For example, to obtain the latex representation $\theta_1$ of the `pol_1` variable, you can run
```python
from causalchamber.ground_truth import latex_name
latex_name('pol_1', enclose=True)

# Output:

# '$\\theta_1$'
```

Setting `enclose=False` will return the name without surrounding `$`.

## Building the chambers

You can find the resources to build the chambers in [`hardware/`](hardware/), together with the datasheets for all physical components (see appendix VI of the original [paper](https://arxiv.org/pdf/2404.11341.pdf)).

## Licenses

All images and `.csv` files in the datasets are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_DATASETS.txt](LICENSE_DATASETS.txt).

The code, e.g., for the `causalchamber` package and mechanistic models, is shared under the [MIT license](https://opensource.org/license/mit/). A copy of the license can also be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).

