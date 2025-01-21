# Dataset: wt\_intake\_impulse\_v1

[<<< Back to all datasets](http://causalchamber.org)

If you use any of the datasets or source code in your work, please consider citing:

```
﻿@article{gamella2025chamber,
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
| [ZIP file](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/wt_intake_impulse_v1.zip) | 8b7a0e587d3e9a804b380d96f14a1b12 |

You can also import the dataset directly into your Python code with the [`causalchamber`](https://pypi.org/project/causalchamber/) package. Install it using pip, e.g.

```
pip install causalchamber
```

Then, load the data from any experiment as follows.

```python
from causalchamber.datasets import Dataset

# Download the dataset and store it, e.g., in the current directory
dataset = Dataset('wt_intake_impulse_v1', root='./', download=True)

# Load the data from an experiment (see experiment names below)
experiment = dataset.get_experiment(name='load_out_0.5_osr_downwind_4')
df = experiment.as_pandas_dataframe()
```

See the table [below](#dataset-description) for all the available experiments and their names.

## Dataset Description

| Chamber     | Configuration |
|:-----------:|:-------------:|
| Wind tunnel | standard      |

The dataset contains a collection of impulse-response curves, where we take measurements of all variables as a short impulse is applied to the intake fan load ($L_\text{in}$), while keeping all other manipulable variables constant. The dataset is used in the OOD generalization case study (task b3) shown in Fig. 5 of the [manuscript](https://arxiv.org/pdf/2404.11341.pdf). This [notebook](https://github.com/juangamella/causal-chamber-paper/blob/main/case_studies/ood_impulses.ipynb) contains the code to reproduce the case study and offers a visualization of the dataset.

The file [variables.csv](variables.csv) contains a brief description of each variable (column) in the `.csv` files; see appendix II of the [manuscript](https://arxiv.org/pdf/2404.11341.pdf) for more details. The table below describes the experiments in the dataset. For a precise description of each experiment protocol, see the corresponding Python script used to generate it.

| Experiment | Generator | Description |
|:----------------------:|:---------:|:------------|
| load\_out\_0.01\_osr\_downwind\_4<br> load\_out\_0.5\_osr\_downwind\_2<br> load\_out\_0.5\_osr\_downwind\_4<br> load\_out\_0.5\_osr\_downwind\_8<br> load\_out\_1\_osr\_downwind\_4  |    [`generators/impulse.py`](generators/impulse.py) | To collect an impulse, we first set the intake fan to idle ($L_\text{in}\leftarrow 0.01$) and set the hatch to a position sampled uniformly at random, i.e., $H \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{0,0.1,\ldots,45\\})$. We wait 500 milliseconds for the chamber pressure to stabilize. Then, we<ol><li>take 5 measurements,</li><li>set the intake fan load to full, i.e. $L_\text{in}\leftarrow 1$,</li><li>take 20 measurements,</li><li>return the intake fan load to idle, i.e. $L_\text{in}\leftarrow 0.01$, and</li><li>take the last 25 measurements.</li></ol>This results in a total of 50 measurements per impulse. In all cases, the measurement frequency is set to ~7 Hz. We collect a total of 5000 impulses, and we repeat the experiment for different values of the exhaust load ($L_\text{out} \in \\{0.01, 0.5, 1\\}$) and oversampling rate of the downwind barometer ($O_\text{dw} \in \\{2, 4, 8\\}$). |



## Changelog

| Dataset version | Date       | Description                     |
|:---------------:|:----------:|:-------------------------------:|
| v1.0            | 25.03.2024 | Initial release of the dataset. |


## Compiling the Experiment Protocols

You can generate the experiment protocols by running `make protocols` in a make-capable machine. This will execute the Python scripts in `generators/` and store the resulting protocols in `protocols/`. The file [`generators/requirements.txt`](generators/requirements.txt) contains the dependencies needed to run the scripts.


## Licenses

We use different licenses for the datasets and software.

### Dataset License

All images and `.csv` files in the dataset are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_DATASETS.txt](LICENSE_DATASETS.txt).

### Software License

All other software, including but not limited to Makefiles and Python scripts, are licensed under the [MIT license](https://opensource.org/license/mit/). A copy of the license can be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).

