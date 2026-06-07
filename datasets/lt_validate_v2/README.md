# Dataset: lt\_validate\_v2

[<<< Back to all datasets](https://github.com/juangamella/causal-chamber)

If you use any of the datasets or source code in your work, please consider citing:

```
@article{gamella2025chamber,
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
| ZIP file | TBD |

You can also import the dataset directly into your Python code with the [`causalchamber`](https://github.com/juangamella/causal-chamber-package) package. Install it using pip, e.g.

```
pip install causalchamber
```

Then, load the data from any experiment as follows.

```python
from causalchamber.datasets import Dataset

# Download the dataset and store it, e.g., in the current directory
dataset = Dataset('lt_validate_v2', root='./', download=True)

# Load the data from an experiment (see experiment names below)
experiment = dataset.get_experiment(name='validate_red')
df = experiment.as_pandas_dataframe()
```

See the table [below](#dataset-description) for all the available experiments and their names.

## Dataset Description

| Chamber              | Configuration    |
|:--------------------:|:----------------:|
| Light Tunnel Mk2     | lt_mk2_standard  |

This dataset contains the randomized experiments to validate the ground-truth graph of the Light Tunnel Mk2 in its standard configuration. The experiments implement the binary-intervention validation procedure: for each manipulable variable, all other manipulable variables are held fixed at their context values while the target is alternated randomly between two levels ($x^A$ and $x^B$). The exact values of $N$, $T$, $x^A$, $x^B$, and context settings for each experiment are given in [`lt_validation_configs.csv`](lt_validation_configs.csv).

This dataset is the Mk2 successor of [`lt_validate_v1`](../lt_validate_v1), which covered the original Light Tunnel prototype. The variable naming differences between the two chambers are documented in the [original prototypes page](https://docs.causalchamber.ai/the-chambers/original-prototypes.md) of the documentation.

The file [variables.csv](variables.csv) contains a description of each variable (column) in the `.csv` files. The table below describes the experiments in the dataset. For a precise description of each experiment protocol, see the corresponding Python script used to generate it.

| Experiment | Generator | Description |
|:----------:|:---------:|:------------|
| validate\_blue<br>validate\_diode\_ir\_1<br>validate\_diode\_ir\_2<br>validate\_diode\_ir\_3<br>validate\_diode\_vis\_1<br>validate\_diode\_vis\_2<br>validate\_diode\_vis\_3<br>validate\_green<br>validate\_led\_1\_ir<br>validate\_led\_1\_uv<br>validate\_led\_2\_ir<br>validate\_led\_2\_uv<br>validate\_led\_3\_ir<br>validate\_led\_3\_uv<br>validate\_offset\_angle\_1<br>validate\_offset\_angle\_2<br>validate\_offset\_current\_led\_1\_ir<br>validate\_offset\_current\_led\_1\_uv<br>validate\_offset\_current\_led\_2\_ir<br>validate\_offset\_current\_led\_2\_uv<br>validate\_offset\_current\_led\_3\_ir<br>validate\_offset\_current\_led\_3\_uv<br>validate\_offset\_current\_ls<br>validate\_offset\_current\_mot\_1<br>validate\_offset\_current\_mot\_2<br>validate\_pol\_1<br>validate\_pol\_2<br>validate\_red<br>validate\_res\_angle\_1<br>validate\_res\_angle\_2<br>validate\_res\_current\_led\_1\_ir<br>validate\_res\_current\_led\_1\_uv<br>validate\_res\_current\_led\_2\_ir<br>validate\_res\_current\_led\_2\_uv<br>validate\_res\_current\_led\_3\_ir<br>validate\_res\_current\_led\_3\_uv<br>validate\_res\_current\_ls<br>validate\_res\_current\_mot\_1<br>validate\_res\_current\_mot\_2<br>validate\_sps\_angle\_1<br>validate\_sps\_angle\_2<br>validate\_sps\_current\_led\_1\_ir<br>validate\_sps\_current\_led\_1\_uv<br>validate\_sps\_current\_led\_2\_ir<br>validate\_sps\_current\_led\_2\_uv<br>validate\_sps\_current\_led\_3\_ir<br>validate\_sps\_current\_led\_3\_uv<br>validate\_sps\_current\_ls<br>validate\_sps\_current\_mot\_1<br>validate\_sps\_current\_mot\_2<br>validate\_t\_ir\_1<br>validate\_t\_ir\_2<br>validate\_t\_ir\_3<br>validate\_t\_vis\_1<br>validate\_t\_vis\_2<br>validate\_t\_vis\_3 | [`generators/binary_interventions.py`](generators/binary_interventions.py) | In each experiment the target variable is repeatedly set to a value chosen randomly between two options ($x^A$ or $x^B$), as described in the validation procedure. All other manipulable variables are held at their context values given in [`lt_validation_configs.csv`](lt_validation_configs.csv). |

## Changelog

| Dataset version | Date       | Description                     |
|:---------------:|:----------:|:-------------------------------:|
| v1.0            | TBD        | Initial release of the dataset. |


## Replicating the experiments using the [Remote Lab](https://causalchamber.ai)

You can collect a fresh copy of the datasets from a Causal Chamber® by running the script [`generators/binary_interventions.py`](generators/binary_interventions.py). You will need to edit the script with your [credentials](https://docs.causalchamber.ai/remote-lab/quickstart) for the Remote Lab; you can request access [here](https://forms.causalchamber.ai/lab). The file [`generators/requirements.txt`](generators/requirements.txt) contains the dependencies needed by the script.


## Licenses

We use different licenses for the datasets and software.

### Dataset License

All images and `.csv` files in the dataset are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_DATASETS.txt](LICENSE_DATASETS.txt).

### Software License

All other software, including but not limited to Makefiles and Python scripts, are licensed under the [MIT license](https://opensource.org/license/mit/). A copy of the license can be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).
