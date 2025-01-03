# Dataset: lt\_interventions\_standard\_v1

[<<< Back to all datasets](http://causalchamber.org)

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
| [ZIP file](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/lt_interventions_standard_v1.zip) | 476664d024f88e8b7640998bb5e9ee33 |

You can also import the dataset directly into your Python code with the [`causalchamber`](https://pypi.org/project/causalchamber/) package. Install it using pip, e.g.

```
pip install causalchamber
```

Then, load the data from any experiment as follows.

```python
from causalchamber.datasets import Dataset

# Download the dataset and store it, e.g., in the current directory
dataset = Dataset('lt_interventions_standard_v1', root='./', download=True)

# Load the data from an experiment (see experiment names below)
experiment = dataset.get_experiment(name='uniform_reference')
df = experiment.as_pandas_dataframe()
```

See the table [below](#dataset-description) for all the available experiments and their names.

## Dataset Description

| Chamber      | Configuration |
|:------------:|:-------------:|
| Light tunnel | standard      |

The dataset contains experiments in which single-target interventions of different strengths are performed on all of the light tunnel's manipulable variables. The light tunnel is operating in its standard configuration. Each experiment corresponds to a different intervention, where the target's distribution is shifted with respect to its *reference* distribution in the `uniform_reference` experiment.

The file [variables.csv](variables.csv) contains a brief description of each variable (column) in the `.csv` files; see appendix II of the [manuscript](https://arxiv.org/pdf/2404.11341.pdf) for more details. The table below describes the experiments in the dataset. For a precise description of each experiment protocol, see the corresponding Python script used to generate it.

| Experiment | Generator | Description |
|:----------------------:|:---------:|:------------|
| uniform\_reference | [`generators/uniform.py`](generators/uniform.py) | We independently sample values for all manipulable variables and take a measurement, repeating this process $N=10^4$ times. The actuators are sampled as follows: $R,G,B \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{0,\ldots,85\\})$; $L_{11}, L_{12}, L_{21}, L_{22}, L_{31}, L_{32} \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{0,\ldots,170\\})$; and $\theta_1, \theta_2 \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{-15,-14.9,\ldots,25\\})$, where $\text{Unif}(S)$ denotes sampling uniformly from $S$. The sensor parameters are set as follows: $O_1, O_2, O_C = 1$; $R_1, R_2, R_C$ = 5; $D^I_1,D^I_2,D^I_3=2$; $D^V_1,D^V_2,D^V_3 = 1$; and $T^V_1,T^V_2,T^V_3,T^I_1,T^I_2,T^I_3 = 3$. |
| uniform\_red\_mid<br>uniform\_green\_mid<br>uniform\_blue\_mid | [`generators/uniform.py`](generators/uniform.py) | We sample $R / G / B \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{86,\ldots,170\\})$ and sample all other manipulable variables as in `uniform_reference`. We collect $N = 1000$ measurements. |
| uniform\_red\_strong<br>uniform\_green\_strong<br>uniform\_blue\_strong | [`generators/uniform.py`](generators/uniform.py) | We sample $R / G / B \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{171,\ldots,255\\})$ and sample all other manipulable variables as in `uniform_reference`. We collect $N = 1000$ measurements. |
| uniform\_pol_1\_mid<br>uniform\_pol_2\_mid | [`generators/uniform.py`](generators/uniform.py) | We sample $\theta_1 / \theta_2 \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{26, 26.1,\ldots,65\\})$ and sample all other manipulable variables as in `uniform_reference`. We collect $N = 1000$ measurements. |
| uniform\_pol_1\_strong<br>uniform\_pol_2\_strong | [`generators/uniform.py`](generators/uniform.py) | We sample $\theta_1 / \theta_2 \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{66, 66.1,\ldots,105\\})$ and sample all other manipulable variables as in `uniform_reference`. We collect $N = 1000$ measurements. |
| uniform_l_11_mid<br>uniform_l_12_mid<br>uniform_l_21_mid<br>uniform_l_22_mid<br>uniform_l_31_mid<br>uniform_l_32_mid | [`generators/uniform.py`](generators/uniform.py) | We sample $L_{11} / L_{12} / L_{21} / L_{22} / L_{31} / L_{32} \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{171,\ldots,255\\})$ and sample all other manipulable variables as in `uniform_reference`. We collect $N = 1000$ measurements. |
| uniform_diode_vis_1_mid<br>uniform_diode_vis_2_mid<br>uniform_diode_vis_3_mid | [`generators/uniform.py`](generators/uniform.py) | We set $D^V_1 / D^V_2 / D^V_3 = 0$ and sample all other manipulable variables as in `uniform_reference`. We collect $N = 1000$ measurements. |
| uniform_diode_ir_1_mid<br>uniform_diode_ir_2_mid<br>uniform_diode_ir_3_mid | [`generators/uniform.py`](generators/uniform.py) | We set $D^I_1 / D^I_2 / D^I_3 = 1$ and sample all other manipulable variables as in `uniform_reference`. We collect $N = 1000$ measurements. |
| uniform_diode_ir_1_strong<br>uniform_diode_ir_2_strong<br>uniform_diode_ir_3_strong | [`generators/uniform.py`](generators/uniform.py) | We set $D^I_1 / D^I_2 / D^I_3 = 0$ and sample all other manipulable variables as in `uniform_reference`. We collect $N = 1000$ measurements. |
| uniform_t_ir_1_weak<br>uniform_t_ir_2_weak<br>uniform_t_ir_3_weak<br>uniform_t_vis_1_weak<br>uniform_t_vis_2_weak<br>uniform_t_vis_3_weak | [`generators/uniform.py`](generators/uniform.py) | We set $T^V_1,T^V_2,T^V_3,T^I_1,T^I_2,T^I_3 = 2$ and sample all other manipulable variables as in `uniform_reference`. We collect $N = 1000$ measurements. |
| uniform_t_ir_1_mid<br>uniform_t_ir_2_mid<br>uniform_t_ir_3_mid<br>uniform_t_vis_1_mid<br>uniform_t_vis_2_mid<br>uniform_t_vis_3_mid | [`generators/uniform.py`](generators/uniform.py) | We set $T^V_1,T^V_2,T^V_3,T^I_1,T^I_2,T^I_3 = 1$ and sample all other manipulable variables as in `uniform_reference`. We collect $N = 1000$ measurements. |
| uniform_t_ir_1_strong<br>uniform_t_ir_2_strong<br>uniform_t_ir_3_strong<br>uniform_t_vis_1_strong<br>uniform_t_vis_2_strong<br>uniform_t_vis_3_strong | [`generators/uniform.py`](generators/uniform.py) | We set $T^V_1,T^V_2,T^V_3,T^I_1,T^I_2,T^I_3 = 0$ and sample all other manipulable variables as in `uniform_reference`. We collect $N = 1000$ measurements. |
| uniform_osr_1_weak<br>uniform_osr_2_weak<br>uniform_osr_c_weak | [`generators/uniform.py`](generators/uniform.py) | We set $O_1, O_2, O_C = 2$ and sample all other manipulable variables as in `uniform_reference`. We collect $N = 1000$ measurements. |
| uniform_osr_1_mid<br>uniform_osr_2_mid<br>uniform_osr_c_mid | [`generators/uniform.py`](generators/uniform.py) | We set $O_1, O_2, O_C = 4$ and sample all other manipulable variables as in `uniform_reference`. We collect $N = 1000$ measurements. |
| uniform_osr_1_strong<br>uniform_osr_2_strong<br>uniform_osr_c_strong | [`generators/uniform.py`](generators/uniform.py) | We set $O_1, O_2, O_C = 8$ and sample all other manipulable variables as in `uniform_reference`. We collect $N = 1000$ measurements. |
| uniform_v_angle_1_mid<br>uniform_v_angle_2_mid<br>uniform_v_c_mid | [`generators/uniform.py`](generators/uniform.py) | We set $R_1, R_2,$ or $R_C = 2.56$ and sample all other manipulable variables as in `uniform_reference`. We collect $N = 1000$ measurements. |
| uniform_v_angle_1_strong<br>uniform_v_angle_2_strong<br>uniform_v_c_strong | [`generators/uniform.py`](generators/uniform.py) | We set $R_1, R_2$ or $R_C = 1.1$ and sample all other manipulable variables as in `uniform_reference`. We collect $N = 1000$ measurements. |

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

All other software, including but not limited to Makefiles and Python scripts, are licensed under the [MIT license](https://opensource.org/license/mit/). A copy of the license can be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).

