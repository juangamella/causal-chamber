# Dataset: lt\_malus\_v1

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
| [ZIP file](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/lt_malus_v1.zip) | cc49b95d85410e0b5ea3bcd1479428e3 |

You can also import the dataset directly into your Python code with the [`causalchamber`](https://pypi.org/project/causalchamber/) package. Install it using pip, e.g.

```
pip install causalchamber
```

Then, load the data from any experiment as follows.

```python
from causalchamber.datasets import Dataset

# Download the dataset and store it, e.g., in the current directory
dataset = Dataset('lt_malus_v1', root='./', download=True)

# Load the data from an experiment (see experiment names below)
experiment = dataset.get_experiment(name='white_255')
df = experiment.as_pandas_dataframe()
```

See the table [below](#dataset-description) for all the available experiments and their names.

## Dataset Description

| Chamber      | Configuration |
|:------------:|:-------------:|
| Light tunnel | standard      |

The dataset contains experiments showing the effect of the polarizer angles ($\theta_1, \theta_2$) on the measurements of the third light-intensity sensor ($\tilde{I}_3, \tilde{V}_3$). In each experiment, we rotate the polarizers to random angles and take a measurement at each position, while keeping all other manipulable variables constant. We do this for different settings of the light source.

The file [variables.csv](variables.csv) contains a brief description of each variable (column) in the `.csv` files; see appendix II of the [manuscript](<https://placehold.co/600x400?text=Placeholder:\nArxiv link!>) for more details. The table below describes the experiments in the dataset. For a precise description of each experiment protocol, see the corresponding Python script used to generate it.

| Experiment | Generator | Description |
|:----------------------:|:---------:|:------------|
|   white\_64<br>white\_128<br>white\_255  | [`generators/malus.py`](lt_malus_v1/generators/malus.py) | We keep the light source color constant, with $R,G,B=64/128/255$. Then, we rotate each polarizer to angles $\theta_1, \theta_2 \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{-90,-89.9,\ldots,90\\})$ and take a measurement, repeating this process for a total of $N=1000$ measurements. |
|   red\_64<br>red\_128<br>red\_255  | [`generators/malus.py`](lt_malus_v1/generators/malus.py) | We keep the light source color constant, with $R=64/128/255$ and $G,B=0$. Then, we rotate each polarizer to angles $\theta_1, \theta_2 \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{-90,-89.9,\ldots,90\\})$ and take a measurement, repeating this process for a total of $N=1000$ measurements. |
|   green\_64<br>green\_128<br>green\_255  | [`generators/malus.py`](lt_malus_v1/generators/malus.py) | We keep the light source color constant, with $G=64/128/255$ and $R,B=0$. Then, we rotate each polarizer to angles $\theta_1, \theta_2 \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{-90,-89.9,\ldots,90\\})$ and take a measurement, repeating this process for a total of $N=1000$ measurements. |
|   blue\_64<br>blue\_128<br>blue\_255  | [`generators/malus.py`](lt_malus_v1/generators/malus.py) | We keep the light source color constant, with $B=64/128/255$ and $R,G=0$. Then, we rotate each polarizer to angles $\theta_1, \theta_2 \overset{\text{i.i.d.}}{\sim} \text{Unif}(\\{-90,-89.9,\ldots,90\\})$ and take a measurement, repeating this process for a total of $N=1000$ measurements. |


## Changelog

| Dataset version | Date       | Description                     |
|:---------------:|:----------:|:-------------------------------:|
| v1.0            | 26.03.2024 | Initial release of the dataset. |

## Compiling the Experiment Protocols

You can generate the experiment protocols by running `make protocols` in a make-capable machine. This will execute the Python scripts in `generators/` and store the resulting protocols in `protocols/`. The file [`generators/requirements.txt`](generators/requirements.txt) contains the dependencies needed to run the scripts.


## Licenses

We use different licenses for the datasets and software.

### Dataset License

All images and `.csv` files in the dataset are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_DATASETS.txt](LICENSE_DATASETS.txt).

### Software License

All other software, including but not limited to Makefiles and Python scripts, are licensed under the [MIT license](https://opensource.org/license/mit/). A copy of the license can be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).

