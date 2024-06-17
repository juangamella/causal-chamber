# Dataset: wt\_walks\_v1

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

| Link                                                                                          | MD5 Checksum                     |
|:---------------------------------------------------------------------------------------------:|:--------------------------------:|
| [ZIP file](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/wt_walks_v1.zip) | ac7ada075c905007e34079494c62db9f |

You can also import the dataset directly into your Python code with the [`causalchamber`](https://pypi.org/project/causalchamber/) package. Install it using pip, e.g.

```
pip install causalchamber
```

Then, load the data from any experiment as follows.

```python
from causalchamber.datasets import Dataset

# Download the dataset and store it, e.g., in the current directory
dataset = Dataset('wt_walks_v1', root='./', download=True)

# Load the data from an experiment (see experiment names below)
experiment = dataset.get_experiment(name='actuators_random_walk_1')
df = experiment.as_pandas_dataframe()
```

See the table [below](#dataset-description) for all the available experiments and their names.

## Dataset Description

| Chamber     | Configuration |
|:-----------:|:-------------:|
| Wind tunnel | standard      |

The dataset contains time-series data collected from the wind tunnel. In each experiment, the manipulable variables of the wind tunnel are set according to different time series, and a measurement is collected from the chamber after each step. Some of the experiments are used in the causal discovery and ICA case studies of the original [paper](https://arxiv.org/pdf/2404.11341.pdf) (tasks a3 and d2 in Fig. 5 and 6, respectively).

The file [variables.csv](variables.csv) contains a brief description of each variable (column) in the `.csv` files; see appendix II of the [manuscript](https://arxiv.org/pdf/2404.11341.pdf) for more details. The table below describes the experiments in the dataset. For a precise description of each experiment protocol, see the corresponding Python script used to generate it.

| Experiment | Generator | Description |
|:----------------------:|:---------:|:------------|
|   actuators\_random\_walk\_seed_*  |    [`generators/actuators_random_walk.py`](wt_walks_v1/generators/actuators_random_walk.py) | Actuators variables ($L_\text{in}, L_\text{out}, H, A_1, A_2$) follow independent random walks while sensor parameters are fixed. We collect $N=10^4$ measurements and repeat for 10 random seeds. |
|   loads\_hatch\_mix\_slow\_run\_* <br>loads\_hatch\_mix\_fast\_run\_*  |    [`generators/loads_hatch_mix.py`](wt_walks_v1/generators/loads_hatch_mix.py) | $L_\text{in}, L_\text{out}, H$ follow a sinusoid and square waves, respectively. `_slow` and `_fast` indicate the frequency of the wave. We collect $N=10^4$ measurements. We repeat the experiment a total of 5 runs. |
| regime\_jumps\_single | [`generators/regime_jumps.py`](wt_walks_v1/generators/regime_jumps.py) | We collect 320K observations where the actuators $L_\text{in}, L_\text{out}, A_1,$ and $A_2$ follow independent random walks. Every 10K observations we enter a new regime where we perform single-target interventions on other variables of the chamber, for a total of 32 regimes. In each regime, we perform either no intervention (with probability 0.3) or a single-target intervention (prob. 0.7) on a variable chosen at random from $\\{H,T_\text{in},T_\text{out},O_\text{up},O_\text{dw},O_\text{amb},O_\text{int},R_\text{in},R_\text{out},R_1,R_2\\}$. At the end of the regime the target is returned to its _base_ value, i.e., its value in the first regime (first 10K observations), which contains no interventions and serves as reference. The regimes are identified by increasing numbers in the `flag` column. The actual targets for each regime can be found in the file [regimes_targets.py](wt_walks_v1/regime_targets.py). Below, we plot some examples of variable trajectories as they are affected by regime transitions. |
| regime\_jumps\_single | [`generators/regime_jumps.py`](wt_walks_v1/generators/regime_jumps.py) |  We collect 320K observations where the actuators $L_\text{in}, L_\text{out}, A_1,$ and $A_2$ follow independent random walks. Every 10K observations we enter a new regime where we perform a multiple-target intervention on other variables of the chamber, for a total of 32 regimes. In each regime, we choose the targets at random from $\\{H,T_\text{in},T_\text{out},O_\text{up},O_\text{dw},O_\text{amb},O_\text{int},R_\text{in},R_\text{out},R_1,R_2\\}$; the number of targets is sampled at random from $0,\ldots,5$, that is, some regimes may not contain any interventions. At the end of the regime the targets are returned to their _base_ values, i.e., their value in the first regime (first 10K observations), which contains no interventions and serves as reference. The regimes are identified by increasing numbers in the `flag` column. The actual targets for each regime can be found in the file [regimes_targets.py](wt_walks_v1/regimes_targets.py). |

## Visualization

Below we plot some variable trajectories from the regime\_jumps\_single experiment, showing the transitions between regimes and how the relationship between an effect and its causes is affected by the intervention on some third variable. The ground-truth graph can be found in Figure 3 of the [original paper](https://arxiv.org/pdf/2404.11341.pdf), and a detailed description of the variables and the causal effects can be found in [Appendices II and III](https://arxiv.org/pdf/2404.11341.pdf), respectively.

## Changelog

| Dataset version | Date       | Description                     |
|:---------------:|:----------:|:-------------------------------:|
| v1.0            | 15.04.2024 | Initial release of the dataset. |
| v1.1            | 17.06.2024 | Added new regime\_jumps\_{single,multi} experiments. |

![](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/regime_jumps_single_1.png)
![](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/regime_jumps_single_5.png)
![](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/regime_jumps_single_27.png)
![](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/regime_jumps_single_31.png)
![](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/regime_jumps_single_3.png) 

## Compiling the Experiment Protocols

You can generate the experiment protocols by running `make protocols` in a make-capable machine. This will execute the Python scripts in `generators/` and store the resulting protocols in `protocols/`. The file [`generators/requirements.txt`](generators/requirements.txt) contains the dependencies needed to run the scripts.

## Licenses

We use different licenses for the datasets and software.

### Dataset License

All images and `.csv` files in the dataset are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_DATASETS.txt](LICENSE_DATASETS.txt).

### Software License

All other software, including but not limited to Makefiles and Python scripts, are licensed under the [MIT license](https://opensource.org/license/mit/). A copy of the license can be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).

