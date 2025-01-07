# Dataset: lt\_test\_v1

[<<< Back to all datasets](https://github.com/juangamella/causal-chamber/tree/main)

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
| [ZIP file](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/lt_test_v1.zip) | 16755c741755c795f609d2e42ea9ee18 |

You can also import the dataset directly into your Python code with the [`causalchamber`](https://pypi.org/project/causalchamber/) package. Install it using pip, e.g.

```
pip install causalchamber
```

Then, load the data from any experiment as follows.

```python
from causalchamber.datasets import Dataset

# Download the dataset and store it, e.g., in the current directory
dataset = Dataset('lt_test_v1', root='./', download=True)

# Load the data from an experiment (see experiment names below)
experiment = dataset.get_experiment(name='angle_sensors')
df = experiment.as_pandas_dataframe()
```

See the table [below](#dataset-description) for all the available experiments and their names.

## Dataset Description

| Chamber  | Configuration |
|:--------:|:-------------:|
| Light tunnel | standard      |

The dataset contains experiments to characterize the different effects between variables in the light tunnel. The data are used for different calibration tasks and for the figures in appendix III of the [manuscript](https://arxiv.org/pdf/2404.11341.pdf).

The file [variables.csv](variables.csv) contains a brief description of each variable (column) in the `.csv` files; see appendix II of the [manuscript](https://arxiv.org/pdf/2404.11341.pdf) for more details. The table below describes the experiments in the dataset. For a precise description of each experiment protocol, see the corresponding Python script used to generate it.

| Experiment | Generator | Description |
|:----------------------:|:---------:|:------------|
| analog\_calibration | [`generators/analog_calibration.py`](generators/analog_calibration.py) | Keeping $R, G, B, \theta_1, \theta_2$ constant, we take measurements at different reference voltages $R_C, R_1, R_2$ to calibrate the actual reference voltages produced by arduino board. The results can be found in Table 3 in appendix II of the [manuscript](https://arxiv.org/pdf/2404.11341.pdf). |
| angle\_sensors | [`generators/angle_sensors.py`](generators/angle_sensors.py) | Take measurements with different reference voltages and oversampling rates of the polarizer angle sensors ($\tilde{\theta}_1, \tilde{\theta}_2$), while progressively increasing the polarizer positions $\theta_1=\theta_2 \in [-180,-179,\ldots,180]$. |
| current\_sensor | [`generators/current_sensor.py`](generators/current_sensor.py) | Set $R=G=B=0$ and collect $N=1000$ measurements for each combination $O_C, R_C \in \\{1,2,4,8\\} \times \\{1.1, 2.56, 5\\}$ |
| ir\_sensors | [`generators/ir_sensors.py`](generators/ir_sensors.py) | Used in Fig. 13 of the original paper to illustrate the effect of the photodiode size and exposure time on the light sensor measurements. For each combination of infrared photodiode size ($D^I_1, D^I_2, D^I_3$) and exposure ($T^I_1, T^I_2, T^I_3$) take $N=500$ measurements where $R {\sim} \text{Unif}(0,\ldots,255)$, $G=B=0$ and all other actuators and parameters are kept constant. |

## Changelog

| Dataset version | Date       | Description                     |
|:---------------:|:----------:|:-------------------------------:|
| v1.0            | 20.03.2024 | Initial release of the dataset. |

## Compiling the Experiment Protocols

You can generate the experiment protocols by running `make protocols` in a make-capable machine. This will execute the Python scripts in `generators/` and store the resulting protocols in `protocols/`. The file [`generators/requirements.txt`](generators/requirements.txt) contains the dependencies needed to run the scripts.


## Licenses

We use different licenses for the datasets and software.

### Dataset License

All images and `.csv` files in the dataset are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_DATASETS.txt](LICENSE_DATASETS.txt).

### Software License

All other software, including but not limited to Makefiles and Python scripts, are licensed under the [MIT license](https://opensource.org/license/mit/). A copy of the license can be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).

