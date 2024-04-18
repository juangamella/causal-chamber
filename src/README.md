# Welcome to the `causalchamber` package

[![PyPI version](https://badge.fury.io/py/causalchamber.svg)](https://badge.fury.io/py/causalchamber)
[![Downloads](https://static.pepy.tech/badge/causalchamber)](https://pepy.tech/project/causalchamber)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![The Causal Chambers: (left) the wind tunnel, and (right) the light tunnel with the front panel removed to show its interior.](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/the_chambers.jpg)

The `causalchamber` package gives you access to [datasets](#accessing-the-datasets), [mechanistic models](#mechanistic-models), and [ground-truth graphs](#causal-ground-truth-graphs) from the causal chamber project. See [causalchamber.org](https://causalchamber.org) for more details.

## Download

You can install the package via pip, i.e. by typing

```
pip install causalchamber
```

in an appropriate shell.


## Accessing the datasets

Datasets can be loaded directly into your Python code. For example, you can load the [`lt_camera_test_v1`](https://github.com/juangamella/causal-chamber/tree/main/datasets/lt_camera_test_v1) image dataset as follows:

```python
import causalchamber.datasets as datasets

# Download the dataset and store it, e.g., in the current directory
dataset = datasets.Dataset(name='lt_camera_test_v1', root='./', download=True)

# Select an experiment and load the observations and images
experiment = dataset.get_experiment(name='palette')
observations = experiment.as_pandas_dataframe()
images = experiment.as_image_array(size='200')
```

If `download=True`, the dataset will be downloaded and stored in the path provided by the `root` argument. If the dataset has already been downloaded it will not be downloaded again.

You can see what datasets are available at [causalchamber.org](https://causalchamber.org) or by typing:

```Python
datasets.list_available()

# Output:
# Available datasets (last changes on 2024-03-26):
# 
#   lt_camera_walks_v1
#   lt_test_v1
#   wt_intake_impulse_v1
#   lt_malus_v1
#   lt_camera_test_v1
#   wt_test_v1
# 
# Visit https://causalchamber.org for a detailed description of each dataset.
```

For the available experiments in each dataset, you can run:
```python
dataset.available_experiments()

# Output:
# ['palette',
#  'polarizer_effect_bright',
#  'polarizer_effect_dark',
#  'pure_colors_bright',
#  'pure_colors_dark']
```

For the available image sizes (only in image datasets):
```python
experiment.available_sizes()

# Output:
# ['200', '500', 'full']
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

The graphs for the causal ground truths given in Fig. 3 of the original [paper](https://arxiv.org/pdf/2404.11341.pdf) can be found as adjacency matrices in  the `ground_truths/` directory of the [project repository](https://github.com/juangamella/causal-chamber). The adjacencies can also be loaded through the `causalchamber` [package](https://pypi.org/project/causalchamber/), e.g., 
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

The chamber identifiers are `wt,lt` for the wind tunnel and light tunnel, respectively. To make it easier to plot graphs and reference them back to the original paper, the latex representation of each variable can be obtained by calling the `latex_name` function. For example, to obtain the latex representation $\theta_1$ of the `pol_1` variable, you can run

```python
from causalchamber.ground_truth import latex_name
latex_name('pol_1', enclose=True)

# Output:

# '$\\theta_1$'
```

Setting `enclose=False` will return the name without surrounding `$`.

### Versioning

Non backward-compatible changes to the API are reflected by a change to the minor or major version number,

> e.g. *code that uses causalchamber==0.1.2 will run with causalchamber==0.1.3, but may not run with causalchamber==0.2.0.*
