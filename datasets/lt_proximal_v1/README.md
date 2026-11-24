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
experiment = dataset.get_experiment(name='weak_confounding_linear_proxy_high_a500')
observations = experiment.as_pandas_dataframe()
```

See the table below for all the available experiments and their names.

## Dataset Description

| Chamber      | Configuration |
|:------------:|:-------------:|
| [Light Tunnel Mk2](https://docs.causalchamber.ai/the-chambers/light-tunnel-mk2) | [standard](https://cchamber-box.s3.eu-central-2.amazonaws.com/config_doc_lt_mk2_standard.pdf) |

This dataset contains the experimental data used in the 2026 paper ["*ProximalFM: Amortized Proximal Causal Inference under Hidden Confounding*"](https://arxiv.org/pdf/2610.08078) by Christophe Muller, Ayub Kharel, Alex Luedtke, Chan Park, Eric Tchetgen Tchetgen, Juan L. Gamella, Rahul G. Krishnan, Ricardo Silva and Jakob Zeitler. The paper proposes ProximalFM, a tabular foundation model that estimates the posterior distribution of the conditional average treatment effect (CATE) when confounders are unobserved and only proxy variables are available. The authors use the [Light Tunnel Mk2](https://docs.causalchamber.ai/the-chambers/light-tunnel-mk2) from Causal Chamber® to evaluate their method on a real, physical system with a known causal graph; see Muller et al. (2026, [Appendix E](https://arxiv.org/pdf/2610.08078#page=76)) for details and [Figure E.4](https://arxiv.org/pdf/2610.08078#page=82) for the results.

In the experiments, the authors [introduce additional causal effects](https://docs.causalchamber.ai/case-studies/causal-inference/generating-real-data-with-a-known-causal-structure#adding-causal-effects) using software control functions that set some of the Chamber's inputs as a function of some of its sensor measurements; see Muller et al. (2026, [Appendix E](https://arxiv.org/pdf/2610.08078#page=76)) and the sampling notebook at [`generators/sampling.ipynb`](generators/sampling.ipynb) for details.

The dataset contains a total of 24 experiments of N = 1000 observations each, resulting from the factorial combination of the following settings (see Muller et al., 2026, [Appendix E](https://arxiv.org/pdf/2610.08078#page=76) for details):

- **Confounding:** weak (green LED, crossed polarisers) or strong (blue LED, `pol_2` = 0).
- **Control functions:** linear or non-linear; see Muller et al. (2026, [Figure E.3](https://arxiv.org/pdf/2610.08078#page=80)).
- **Proxy informativeness:** high, (k<sub>Z</sub>, k<sub>W</sub>) = (0, 0); intermediate, (k<sub>Z</sub>, k<sub>W</sub>) = (0.75, 0.75); or low, (k<sub>Z</sub>, k<sub>W</sub>) = (2, 2).\*
- **Treatment strength:** a<sub>1</sub> = 350 or a<sub>1</sub> = 500.

\* The experiments `strong_confounding_linear_proxy_low_a500` and `strong_confounding_linear_proxy_low_a350` use (k<sub>Z</sub>, k<sub>W</sub>) = (0.6, 2.5) instead, to retain a measurable confounding signal; see the paragraph *Treatment and proxy-information settings* in Muller et al. (2026, [Appendix E](https://arxiv.org/pdf/2610.08078#page=77)).

The Chamber variables (see Variable Table in the [documentation](https://cchamber-box.s3.eu-central-2.amazonaws.com/config_doc_lt_mk2_standard.pdf)) map to the variables in the paper (see Muller et al., 2026, [Figures E.1](https://arxiv.org/pdf/2610.08078#page=76) and [E.2](https://arxiv.org/pdf/2610.08078#page=79)) as follows: U = `green` (the drive of the confounder LED; in the strong-confounding settings this value is applied to the `blue` LED but still stored in the `green` column), X = `red`, Z = `led_2_uv`, W = `pol_1`, A = `led_3_uv > 0`, Y = `ir_3`. The columns `Y0` and `Y1` contain the counterfactual outcomes, and `pA` the true propensity score.

To obtain a dataframe with the variable names used in the paper, you can run:

```python
df = experiment.as_pandas_dataframe()
df = df.rename(columns={'green': 'U', 'red': 'X', 'led_2_uv': 'Z', 'pol_1': 'W', 'ir_3': 'Y'})
df['A'] = (df['led_3_uv'] > 0).astype(int)
```

The table below describes the experiments in the dataset.

| Experiment             | Generator                                    | Description |
|:----------------------:|:--------------------------------------------:|:------------|
| weak\_confounding\_linear\_proxy\_high\_a500 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Weak confounding (green LED, crossed polarisers), linear control functions, high proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (0, 0), treatment strength a<sub>1</sub> = 500. |
| weak\_confounding\_linear\_proxy\_mid\_a500 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Weak confounding (green LED, crossed polarisers), linear control functions, intermediate proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (0.75, 0.75), treatment strength a<sub>1</sub> = 500. |
| weak\_confounding\_linear\_proxy\_low\_a500 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Weak confounding (green LED, crossed polarisers), linear control functions, low proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (2, 2), treatment strength a<sub>1</sub> = 500. |
| weak\_confounding\_non\_linear\_proxy\_high\_a500 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Weak confounding (green LED, crossed polarisers), non-linear control functions, high proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (0, 0), treatment strength a<sub>1</sub> = 500. |
| weak\_confounding\_non\_linear\_proxy\_mid\_a500 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Weak confounding (green LED, crossed polarisers), non-linear control functions, intermediate proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (0.75, 0.75), treatment strength a<sub>1</sub> = 500. |
| weak\_confounding\_non\_linear\_proxy\_low\_a500 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Weak confounding (green LED, crossed polarisers), non-linear control functions, low proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (2, 2), treatment strength a<sub>1</sub> = 500. |
| strong\_confounding\_linear\_proxy\_high\_a500 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Strong confounding (blue LED, `pol_2` = 0), linear control functions, high proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (0, 0), treatment strength a<sub>1</sub> = 500. |
| strong\_confounding\_linear\_proxy\_mid\_a500 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Strong confounding (blue LED, `pol_2` = 0), linear control functions, intermediate proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (0.75, 0.75), treatment strength a<sub>1</sub> = 500. |
| strong\_confounding\_linear\_proxy\_low\_a500 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Strong confounding (blue LED, `pol_2` = 0), linear control functions, low proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (0.6, 2.5), treatment strength a<sub>1</sub> = 500. |
| strong\_confounding\_non\_linear\_proxy\_high\_a500 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Strong confounding (blue LED, `pol_2` = 0), non-linear control functions, high proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (0, 0), treatment strength a<sub>1</sub> = 500. |
| strong\_confounding\_non\_linear\_proxy\_mid\_a500 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Strong confounding (blue LED, `pol_2` = 0), non-linear control functions, intermediate proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (0.75, 0.75), treatment strength a<sub>1</sub> = 500. |
| strong\_confounding\_non\_linear\_proxy\_low\_a500 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Strong confounding (blue LED, `pol_2` = 0), non-linear control functions, low proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (2, 2), treatment strength a<sub>1</sub> = 500. |
| weak\_confounding\_linear\_proxy\_high\_a350 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Weak confounding (green LED, crossed polarisers), linear control functions, high proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (0, 0), treatment strength a<sub>1</sub> = 350. |
| weak\_confounding\_linear\_proxy\_mid\_a350 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Weak confounding (green LED, crossed polarisers), linear control functions, intermediate proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (0.75, 0.75), treatment strength a<sub>1</sub> = 350. |
| weak\_confounding\_linear\_proxy\_low\_a350 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Weak confounding (green LED, crossed polarisers), linear control functions, low proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (2, 2), treatment strength a<sub>1</sub> = 350. |
| weak\_confounding\_non\_linear\_proxy\_high\_a350 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Weak confounding (green LED, crossed polarisers), non-linear control functions, high proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (0, 0), treatment strength a<sub>1</sub> = 350. |
| weak\_confounding\_non\_linear\_proxy\_mid\_a350 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Weak confounding (green LED, crossed polarisers), non-linear control functions, intermediate proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (0.75, 0.75), treatment strength a<sub>1</sub> = 350. |
| weak\_confounding\_non\_linear\_proxy\_low\_a350 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Weak confounding (green LED, crossed polarisers), non-linear control functions, low proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (2, 2), treatment strength a<sub>1</sub> = 350. |
| strong\_confounding\_linear\_proxy\_high\_a350 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Strong confounding (blue LED, `pol_2` = 0), linear control functions, high proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (0, 0), treatment strength a<sub>1</sub> = 350. |
| strong\_confounding\_linear\_proxy\_mid\_a350 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Strong confounding (blue LED, `pol_2` = 0), linear control functions, intermediate proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (0.75, 0.75), treatment strength a<sub>1</sub> = 350. |
| strong\_confounding\_linear\_proxy\_low\_a350 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Strong confounding (blue LED, `pol_2` = 0), linear control functions, low proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (0.6, 2.5), treatment strength a<sub>1</sub> = 350. |
| strong\_confounding\_non\_linear\_proxy\_high\_a350 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Strong confounding (blue LED, `pol_2` = 0), non-linear control functions, high proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (0, 0), treatment strength a<sub>1</sub> = 350. |
| strong\_confounding\_non\_linear\_proxy\_mid\_a350 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Strong confounding (blue LED, `pol_2` = 0), non-linear control functions, intermediate proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (0.75, 0.75), treatment strength a<sub>1</sub> = 350. |
| strong\_confounding\_non\_linear\_proxy\_low\_a350 | [`generators/sampling.ipynb`](generators/sampling.ipynb) | Strong confounding (blue LED, `pol_2` = 0), non-linear control functions, low proxy informativeness with (k<sub>Z</sub>, k<sub>W</sub>) = (2, 2), treatment strength a<sub>1</sub> = 350. |

**Note on file names.** The notebook [`generators/sampling.ipynb`](generators/sampling.ipynb) writes each experiment to a file named `out_binaryA_counterfactuals_<setting>_proxy_<level>_<suffix>.csv`, where the suffix is `smoothA` for a<sub>1</sub> = 500 and `smoothA_a350` for a<sub>1</sub> = 350. The experiment names drop the `out_binaryA_counterfactuals_` prefix and replace the suffix with `a500` or `a350`, respectively. For example, the notebook output `out_binaryA_counterfactuals_weak_confounding_linear_proxy_high_smoothA.csv` corresponds to the experiment `weak_confounding_linear_proxy_high_a500`, and `out_binaryA_counterfactuals_weak_confounding_linear_proxy_high_smoothA_a350.csv` to `weak_confounding_linear_proxy_high_a350`.

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
