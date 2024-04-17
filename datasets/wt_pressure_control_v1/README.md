# Dataset: wt\_pressure\_control\_v1

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

| Link                 | MD5 Checksum |
|:--------------------:|:------------:|
| [ZIP file](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/wt_pressure_control_v1.zip) | 8cb1c9bf19cedc5baea7a9c15e54af6a |

You can also import the dataset directly into your Python code with the [`causalchamber`](https://pypi.org/project/causalchamber/) package. Install it using pip, e.g.

```
pip install causalchamber
```

Then, load the data from any experiment as follows.

```python
from causalchamber.datasets import Dataset

# Download the dataset and store it, e.g., in the current directory
dataset = Dataset('wt_pressure_control_v1', root='./', download=True)

# Load the data from an experiment (see experiment names below)
experiment = dataset.get_experiment(name='hatch_0')
df = experiment.as_pandas_dataframe()
```

See the table [below](#dataset-description) for all the available experiments and their names.

## Dataset Description

| Chamber     | Configuration    |
|:-----------:|:----------------:|
| Wind tunnel | pressure-control |

This dataset contains experiments collected from the wind tunnel in its _pressure-control_ configuration, where the fan loads $`L_\text{in}, L_\text{out}`$ are set by a PID controller to keep the pressure measurement at the downwind barometer ($`\tilde{P}_\text{dw}`$) constant. More details about the control mechanism can be found in section 3 and appendix III of the original [paper](<https://placehold.co/600x400?text=Placeholder:\nArxiv link!>).

The file [variables.csv](variables.csv) contains a brief description of each variable (column) in the `.csv` files; see appendix II of the [manuscript](<https://placehold.co/600x400?text=Placeholder:\nArxiv link!>) for more details. The table below describes the experiments in the dataset. For a precise description of each experiment protocol, see the corresponding Python script used to generate it.

| Experiment | Generator                                                     | Description |
|:----------:|:-------------------------------------------------------------:|:------------|
| hatch\_0   | [`generators/hatch.py`](wt_pressure_control_v1/generators/hatch.py) | The hatch is closed ($H=0$) and all other exogenous, manipulable variables of the system (i.e. all actuators and sensor parameters except $L_\text{in}, L_\text{out}$) are kept at a constant value while $N=10000$  measurements are collected. The control target for the pressure of the downwind barometer ($`\tilde{P}_\text{dw}`$) corresponds to the pressure measured when powering up the chamber. |

## Changelog

| Dataset version | Date       | Description                     |
|:---------------:|:----------:|:-------------------------------:|
| v1.0            | 16.04.2024 | Initial release of the dataset. |


## Compiling the Experiment Protocols

You can generate the experiment protocols by running `make protocols` in a make-capable machine. This will execute the Python scripts in `generators/` and store the resulting protocols in `protocols/`. The file [`generators/requirements.txt`](generators/requirements.txt) contains the dependencies needed to run the scripts.


## Licenses

We use different licenses for the datasets and software.

### Dataset License

All images and `.csv` files in the dataset are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_DATASETS.txt](LICENSE_DATASETS.txt).

### Software License

All other software, including but not limited to Makefiles and Python scripts, is licensed under the [MIT license](https://opensource.org/license/mit/). A copy of the license can be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).

