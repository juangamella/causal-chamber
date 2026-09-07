# Building the chambers

[![PyPI version](https://badge.fury.io/py/causalchamber.svg)](https://badge.fury.io/py/causalchamber)
[![Downloads](https://static.pepy.tech/badge/causalchamber)](https://pepy.tech/project/causalchamber)
[![License: CC-BY 4.0](https://img.shields.io/static/v1.svg?logo=creativecommons&logoColor=white&label=License&message=CC-BY%204.0&color=yellow)](https://creativecommons.org/licenses/by/4.0/)
[![Donate](https://img.shields.io/static/v1.svg?logo=Github%20Sponsors&label=donate&message=Github%20Sponsors&color=e874ff)](https://github.com/sponsors/juangamella)

![The Causal Chambers: (left) the wind tunnel, and (right) the light tunnel with the front panel removed to show its interior.](https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/the_chambers.jpg)

Here you can find the resources to build the wind tunnel and light tunnel prototypes (Mk 1) described in the original [paper](https://www.nature.com/articles/s42256-024-00964-x).

- [`arduino/`](arduino/) contains the code for the arduino boards that control each chamber
- [`control/`](control/) contains the python code to connect your computer to the chambers and run experiments
- [`lasercuts/`](lasercuts/) contains the lasercutter diagrams
- [`schematics/`](schematics/) contains the bill of materials and schematics for the electronics of each chamber

> [!TIP]
> We're preparing to release the build resources for the [Mk2 chambers](https://docs.causalchamber.ai/the-chambers/how-they-work), the newer version we use in our [Remote Lab](https://causalchamber.ai).

## Disclaimer

To build the chambers you will need some common assembly tools and access to some more specialized equipment: a laser cutter of sufficient size and an electronics bench (for soldering and testing). We assume that you already posses the pertinent knowledge to use them.

> [!WARNING]
> Since publication, some of the components needed for the prototypes are no longer manufactured. You will need to find a replacement for the ACS70331 2.5A current sensor. Depending on where you live, the Grove chips with the DPS310 barometers may also be difficult to find (see [here](https://wiki.seeedstudio.com/Sensor_barometer/) for alternatives).

## Remote Lab API

We maintain a pool of chambers that you can operate in real-time using in our Remote Lab API. Visit [causalchamber.ai](https://causalchamber.ai/) for more information.

## Licenses

The resources to build the hardware, that is, the blueprints, schematics, component lists and the arduino and control code, are shared under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). This means you are free to use, share and modify them as long as you give appropriate credit and communicate changes.

If you use these resources in your scientific work, please consider citing:

```
﻿@article{gamella2025chamber,
  author={Gamella, Juan L. and Peters, Jonas and B{\"u}hlmann, Peter},
  title={Causal chambers as a real-world physical testbed for {AI} methodology},
  journal={Nature Machine Intelligence},
  doi={10.1038/s42256-024-00964-x},
  year={2025},
}
```
