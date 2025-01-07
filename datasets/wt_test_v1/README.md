# Dataset: wt\_test\_v1

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
| [ZIP file](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/wt_test_v1.zip) | 5eed621f5b54e431c4442fc9cc947db6 |

You can also import the dataset directly into your Python code with the [`causalchamber`](https://pypi.org/project/causalchamber/) package. Install it using pip, e.g.

```
pip install causalchamber
```

Then, load the data from any experiment as follows.

```python
from causalchamber.datasets import Dataset

# Download the dataset and store it, e.g., in the current directory
dataset = Dataset('wt_test_v1', root='./', download=True)

# Load the data from an experiment (see experiment names below)
experiment = dataset.get_experiment(name="no_load")
df = experiment.as_pandas_dataframe()
```

See the table [below](#dataset-description) for all the available experiments and their names.

## Dataset Description

| Chamber     | Configuration |
|:-----------:|:-------------:|
| Wind tunnel | standard      |

The dataset contains experiments to characterize the different effects between variables in the wind tunnel. The data are used for different calibration tasks and for the figures in appendix III of the [manuscript](https://arxiv.org/pdf/2404.11341.pdf).

The file [variables.csv](variables.csv) contains a brief description of each variable (column) in the `.csv` files; see appendix II of the [manuscript](https://arxiv.org/pdf/2404.11341.pdf) for more details. The table below describes the experiments in the dataset. For a precise description of each experiment protocol, see the corresponding Python script used to generate it.

| Experiment | Generator | Description |
|:----------------------:|:---------:|:------------|
| analog\_calibration | [`generators/analog_calibration.py`](generators/analog_calibration.py) | Keeping $L_\text{in}, L_\text{out}, A_1, A_2$ constant, we take measurements at different reference voltages $R_\text{in}, R_\text{out}, R_1, R_2$ to calibrate the actual reference voltages produced by arduino board. The results can be found in Table 3 in appendix II of the [manuscript](https://arxiv.org/pdf/2404.11341.pdf). |
| mic\_effects | [`generators/mic_effects.py`](generators/mic_effects.py) | Take measurements under different inputs to $L_\text{in}, L_\text{out}, H$ while keeping all other actuators and sensor parameters constant. Used in Fig. 10 to illustrate the effect of the fan loads $L_\text{in}, L_\text{out}$ and hatch position $H$ on the microphone readings. |
| no\_load | [`generators/no_load.py`](generators/no_load.py) | Set $L_\text{in} = L_\text{out} = 0$ and take measurements while keeping all other manipulable variables constant. Used to estimate the no-load current of the fans. |
| osr\_barometers | [`generators/osr_barometers.py`](generators/osr_barometers.py) | While keeping all other actuators and sensor parameters constant, take measurements under different oversampling rates of the barometers ($O_\textnormal{up}, O_\textnormal{dw}, O_\textnormal{amb}, O_\textnormal{int}$). |
| osr\_mic | [`generators/osr_mic.py`](generators/osr_mic.py) | While keeping all other actuators and sensor parameters constant, take measurements under different oversampling rates $O_M$ of the microphone. |
| potis\_coarse<br>potis\_fine | [`generators/potentiometers.py`](generators/potentiometers.py) | Take measurements while progressively increasing the potentiometer settings $A_1, A_2$ and keeping all other actuators and sensor parameters constant. The variant coarse/fine determines the size of the increase at each step.  |
| steps | [`generators/steps.py`](generators/steps.py) | Applies a step signal to $L_\text{in}, H$ and $L_\text{out}$. The data is used in figure 6e of the [paper](https://arxiv.org/pdf/2404.11341.pdf) to illustrate the behaviour of the wind tunnel models. |
| tach\_resolution | [`generators/tach_resolution.py`](generators/tach_resolution.py) | Take measurements for $T_\text{in} = 0$ and $T_\text{in} = 1$, under a progressive increase in the fan load $L_\text{in}$. Used in Fig. 8 to illustrate the effect of the tachometer resolutions $T_\text{in}, T_\text{out}$  |
| zero\_load | [`generators/zero_load.py`](generators/zero_load.py) | Power off the exhaust fan ($L_\text{out}\leftarrow 0$) mid-way through applying an impulse to the intake fan load $L_\text{in}$. Used in Fig. 11 of appendix III to show the effect that powering off a fan has on the corresponding speed measurement. |

## Changelog

| Dataset version | Date       | Description                     |
|:---------------:|:----------:|:-------------------------------:|
| v1.0            | 14.04.2024 | Initial release of the dataset. |

## Compiling the Experiment Protocols

You can generate the experiment protocols by running `make protocols` in a make-capable machine. This will execute the Python scripts in `generators/` and store the resulting protocols in `protocols/`. The file [`generators/requirements.txt`](generators/requirements.txt) contains the dependencies needed to run the scripts.


## Licenses

We use different licenses for the datasets and software.

### Dataset License

All images and `.csv` files in the dataset are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_DATASETS.txt](LICENSE_DATASETS.txt).

### Software License
All other software, including but not limited to Makefiles and Python scripts, is licensed under the [MIT license](https://opensource.org/license/mit/). A copy of the license can be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).

