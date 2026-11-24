# Dataset: lt\_proximal\_v1

[<<< Back to all datasets](https://github.com/juangamella/causal-chamber)

If you use any of the datasets or source code in your work, please consider citing:

```
@article{muller2026proximalfm,
  title={ProximalFM: Amortized Proximal Causal Inference under Hidden Confounding},
  author={Muller, Christophe and Kharel, Ayub and Luedtke, Alex and Park, Chan and Tchetgen Tchetgen, Eric and Gamella, Juan L. and Krishnan, Rahul G. and Silva, Ricardo and Zeitler, Jakob},
  journal={arXiv preprint arXiv:2610.08078},
  year={2026}
}
```

and

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
| [ZIP file](TODO) | TODO |

You can also import the dataset directly into your Python code with the [`causalchamber`](https://github.com/juangamella/causal-chamber-package) package. Install it using pip, e.g.

```
pip install causalchamber
```

Then, load the data from any experiment as follows.

```python
from causalchamber.datasets import Dataset

# Download the dataset and store it, e.g., in the current directory
dataset = Dataset('lt_proximal_v1', root='./', download=True)

# Load the observations from an experiment (see experiment names below)
experiment = dataset.get_experiment(name='TODO')
observations = experiment.as_pandas_dataframe()
```

See the table below for all the available experiments and their names.

## Dataset Description

| Chamber      | Configuration |
|:------------:|:-------------:|
| [Light Tunnel Mk2](https://docs.causalchamber.ai/the-chambers/light-tunnel-mk2) | [standard](https://cchamber-box.s3.eu-central-2.amazonaws.com/config_doc_lt_mk2_standard.pdf) |

This dataset contains the experimental data used in the 2026 paper ["*ProximalFM: Amortized Proximal Causal Inference under Hidden Confounding*"](https://arxiv.org/pdf/2610.08078) by Christophe Muller, Ayub Kharel, Alex Luedtke, Chan Park, Eric Tchetgen Tchetgen, Juan L. Gamella, Rahul G. Krishnan, Ricardo Silva and Jakob Zeitler. The paper proposes ProximalFM, a tabular foundation model that estimates the posterior distribution of the conditional average treatment effect (CATE) when confounders are unobserved and only proxy variables are available. The authors use the [Light Tunnel Mk2](https://docs.causalchamber.ai/the-chambers/light-tunnel-mk2) from Causal Chamber® to evaluate their method on a real, physical system with a known causal graph; see Muller et al. (2026, [Appendix E](https://arxiv.org/pdf/2610.08078#page=76)) for details.

See the [documentation](https://cchamber-box.s3.eu-central-2.amazonaws.com/config_doc_lt_mk2_standard.pdf) of the standard configuration for a detailed description of the Chamber variables. In the experiments, the authors [introduce additional causal effects](https://docs.causalchamber.ai/case-studies/causal-inference/generating-real-data-with-a-known-causal-structure#adding-causal-effects) using software control functions that set some of the Chamber's inputs as a function of some of its sensor measurements; see Muller et al. (2026, [Appendix E](https://arxiv.org/pdf/2610.08078#page=76)) and the sampling notebook at [`generators/sampling.ipynb`](generators/sampling.ipynb) for details. The table below describes the experiments in the dataset.

| Experiment             | Generator                                    | Description |
|:----------------------:|:--------------------------------------------:|:------------|
| TODO | [`generators/sampling.ipynb`](generators/sampling.ipynb) | TODO |

## Changelog

| Dataset version | Date       | Description                                             |
|:---------------:|:----------:|:-------------------------------------------------------:|
| v1.0            | 24.11.2026 | Initial release of the dataset.                         |

## Replicating the experiments using the [Remote Lab](https://docs.causalchamber.ai/remote-lab/quickstart)

You can collect a fresh copy of the datasets from a Causal Chamber® by running the notebook [`generators/sampling.ipynb`](generators/sampling.ipynb). You will need to edit the notebook with your [credentials](https://docs.causalchamber.ai/remote-lab/quickstart) for the Remote Lab; you can request access [here](https://forms.causalchamber.ai/lab). The file [`generators/requirements.txt`](generators/requirements.txt) contains the dependencies needed by the notebook.

## Licenses

We use different licenses for the datasets and software.

### Dataset License

All `.csv` files in the dataset are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_DATASETS.txt](LICENSE_DATASETS.txt).

### Software License

All other software, including but not limited to Makefiles and Python scripts, are licensed under the [MIT license](https://opensource.org/license/mit/). A copy of the license can be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).
