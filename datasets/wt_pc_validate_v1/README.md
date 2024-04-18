# Dataset: wt\_pc\_validate\_v1

[<<< Back to all datasets](http://causalchamber.org)

If you use any of the datasets or source code in your work, please consider citing:

```
@article{gamella2024chamber,
  title={The Causal Chambers: Real Physical Systems as a Testbed for AI Methodology},
  author={Gamella, Juan L. and B\"uhlmann, Peter and Peters, Jonas},
  journal={arXiv preprint arXiv:TODO},
  year={2024}
}
```

## Download

| Link     | MD5 Checksum                     |
|:--------:|:--------------------------------:|
| [ZIP file](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/wt_pc_validate_v1.zip) | 3763de7a1a2715d5789d6e95464249c0 |

You can also import the dataset directly into your Python code with the [`causalchamber`](https://pypi.org/project/causalchamber/) package. Install it using pip, e.g.

```
pip install causalchamber
```

Then, load the data from any experiment as follows.

```python
from causalchamber.datasets import Dataset

# Download the dataset and store it, e.g., in the current directory
dataset = Dataset('wt_pc_validate_v1', root='./', download=True)

# Load the data from an experiment (see experiment names below)
experiment = dataset.get_experiment(name='validate_pressure_downwind_loads')
df = experiment.as_pandas_dataframe()
```

See the table [below](#dataset-description) for all the available experiments and their names.

## Dataset Description

| Chamber     | Configuration    |
|:-----------:|:----------------:|
| Wind tunnel | pressure-control |

This dataset contains the randomized experiments to validate the ground-truth graph of the wind tunnel in its _pressure-control_ configuration (Fig. 3d of the original [paper](<https://placehold.co/600x400?text=Placeholder:\nArxiv link!>)). The experiments in the dataset correspond to the validation procedure described in appendix V of the manuscript. For each edge, the values for $N, T, x^A, x^B$ are given in the file [`wt_pc_validation_configs.csv`](wt_pc_validate_v1/wt_pc_validation_configs.csv). The code to obtain the p-values shown in the tables of appendix V can be found in the separate [paper repository](https://github.com/juangamella/causal-chamber-paper).


The file [variables.csv](variables.csv) contains a brief description of each variable (column) in the `.csv` files; see appendix II of the [manuscript](<https://placehold.co/600x400?text=Placeholder:\nArxiv link!>) for more details. The table below describes the experiments in the dataset. For a precise description of each experiment protocol, see the corresponding Python script used to generate it.

| Experiment | Generator | Description |
|:----------------------:|:---------:|:------------|
| validate\_pressure\_downwind\_loads | [`generators/binary_interventions.py`](wt_pc_validate_v1/generators/binary_interventions.py) | In each experiment we repeatedly set the manipulable variable given in the experiment name to a value picked randomly between two options ($x^A$ or $x^B$), as described in the validation procedure given in appendix V of the [manuscript](<https://placehold.co/600x400?text=Placeholder:\nArxiv link!>). |

## Changelog

| Dataset version | Date       | Description                     |
|:---------------:|:----------:|:-------------------------------:|
| v1.0            | 17.04.2024 | Initial release of the dataset. |

## Compiling the Experiment Protocols

You can generate the experiment protocols by running `make protocols` in a make-capable machine. This will execute the Python scripts in `generators/` and store the resulting protocols in `protocols/`. The file [`generators/requirements.txt`](generators/requirements.txt) contains the dependencies needed to run the scripts.


## Licenses

We use different licenses for the datasets and software.

### Dataset License

All images and `.csv` files in the dataset are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_DATASETS.txt](LICENSE_DATASETS.txt).

### Software License

All other software, including but not limited to Makefiles and Python scripts, are licensed under the [MIT license](https://opensource.org/license/mit/). A copy of the license can be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).

