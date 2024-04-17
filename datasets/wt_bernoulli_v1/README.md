# Dataset: wt\_bernoulli\_v1

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
| [ZIP file](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/wt_bernoulli_v1.zip) | 00d6abbdf42ed953ca94dc107067ea56 |

You can also import the dataset directly into your Python code with the [`causalchamber`](https://pypi.org/project/causalchamber/) package. Install it using pip, e.g.

```
pip install causalchamber
```

Then, load the data from any experiment as follows.

```python
from causalchamber.datasets import Dataset

# Download the dataset and store it, e.g., in the current directory
dataset = Dataset('wt_bernoulli_v1', root='./', download=True)

# Load the data from an experiment (see experiment names below)
experiment = dataset.get_experiment(name='random_loads_both')
df = experiment.as_pandas_dataframe()
```

See the table [below](#dataset-description) for all the available experiments and their names.

## Dataset Description

| Chamber     | Configuration |
|:-----------:|:-------------:|
| Wind tunnel | standard      |

The dataset contains experiments to show Bernoulli's principle in the difference between the measurements of the up- and downwind barometers. The effect is described in appendix IV.1.3 of the [manuscript](<https://placehold.co/600x400?text=Placeholder:\nArxiv link!>). The dataset is used for the symbolic regression task in Fig. 6e.

The file [variables.csv](variables.csv) contains a brief description of each variable (column) in the `.csv` files; see appendix II of the [manuscript](<https://placehold.co/600x400?text=Placeholder:\nArxiv link!>) for more details. The table below describes the experiments in the dataset. For a precise description of each experiment protocol, see the corresponding Python script used to generate it.

| Experiment            | Generator                                                                                | Description |
|:---------------------:|:----------------------------------------------------------------------------------------:|:------------|
| fans\_off             | [`generators/fans_off.py`](wt_bernoulli_v1/generators/fans_off.py)                       | We completely power off both fans ($L_\text{in} = L_\text{out} = 0$) and take $N=5000$ measurements while keeping all other actuators and sensor parameters constant. The data can be used to estimate the manufacturing offset between the up- and downwind barometer readings ($`\tilde{P}_\text{up}, \tilde{P}_\text{dw}`$), as the barometers are at the same height and with no airflow the air pressure at both is the same. | 
| random\_loads\_both   | [`generators/random_loads_both.py`](wt_bernoulli_v1/generators/random_loads_both.py)     | Set both loads to a value sampled at random, i.e., $L_\text{in} = L_\text{out} \sim \text{Unif}([0,1])$, wait 8 seconds for the system to stabilize, and collect 100 measurements while keeping all other actuators and sensor parameters constant. The process is repeated 2000 times. |
| random\_loads\_intake | [`generators/random_loads_intake.py`](wt_bernoulli_v1/generators/random_loads_intake.py) | Same as the previous experiment, but the load of the exhaust fan is kept constant at $L_\text{out}=0.1$. |

## Changelog

| Dataset version | Date       | Description                     |
|:---------------:|:----------:|:-------------------------------:|
| v1.0            | 15.04.2024 | Initial release of the dataset. |


## Compiling the Experiment Protocols

You can generate the experiment protocols by running `make protocols` in a make-capable machine. This will execute the Python scripts in `generators/` and store the resulting protocols in `protocols/`. The file [`generators/requirements.txt`](generators/requirements.txt) contains the dependencies needed to run the scripts.


## Licenses

We use different licenses for the datasets and software.

### Dataset License

All images and `.csv` files in the dataset are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_DATASETS.txt](LICENSE_DATASETS.txt).

### Software License

All other software, including but not limited to Makefiles and Python scripts, are licensed under the [MIT license](https://opensource.org/license/mit/). A copy of the license can be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).

