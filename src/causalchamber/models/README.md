# Mechanistic Models: Python Implementation

A description of each model and its derivation is given in appendix IV of the original [paper](XXXXX). The models and the input parameters follow the nomenclature in the paper, which we recommend reading alongside the implementation. The code is organized as follows:

- [`wind_tunnel_models.py`](wind_tunnel_models.py) contains models A1, A2, B1, C1, C2 and C3
- [`wind_tunnel_simulators.py`](wind_tunnel_simulators.py) contains the simulators of fan speeds and air pressure showin in shown in Fig. 6f of the [paper](XXXXX).
- [`light_tunnel_models.py`](light_tunnel_models.py) contains model E1
- [`image_capture.py`](image_capture.py) contains models F1, F2 and F3 of the image capture process (output shown in Fig. 6f of the [paper](XXXXX)).

Model D1 of the difference between the readings of the up- and downwind barometers is not implemented and is used only as a ground-truth for the symbolic regression task shown in Fig. 6e of the [paper](XXXXX).

If you use the models in your scientific work, please consider citing:

```
@article{gamella2024chamber,
  title={The Causal Chambers: Real Physical Systems as a Testbed for AI Methodology},
  author={Gamella, Juan L. and B\"uhlmann, Peter and Peters, Jonas},
  journal={(work in progress)},
  year={2023}
}
```
