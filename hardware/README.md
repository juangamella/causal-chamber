# Building the Chambers

Here you can find the resources to build the wind tunnel and light tunnel described in the original [paper](https://arxiv.org/pdf/2404.11341.pdf). In particular,

- [`blueprints/`](blueprints/) contains the laser cutter designs for the framework and enclosures of the chambers.
- [`electronics/`](blueprints/) contains the schematics for the electronic components of the chambers.
- [`component_list.md`](component_list.md) contains a list of all necessary components to build each chamber, including all the sensors and the camera.
- [`arduino/`](arduino/) contains the code that runs on the control computers aboard the chambers, including all necessary libraries.
- [`control/`](control/) contains the Python application to send commands and receive data from the chambers.
- [`datasheets/`](datasheets/) contains the datasheets for all components, outlined in appendix VI of the original [paper](https://arxiv.org/pdf/2404.11341.pdf).

**Note**: We are still working on the blueprints, electronics diagrams and component lists for the latest version of the chambers. Please check again soon or shoot us (Juan) an email!

## Disclaimer

To build the chambers you will need some common assembly tools and access to some more specialized equipment: a laser cutter of sufficient size and an electronics bench (for soldering and testing). We assume that you already posses the pertinent knowledge to use them.

If you would like to build the chambers but lack the necessary skills, time, or equipment, we can build them for you for a fee. Please reach out to [Juan L. Gamella](mailto:juan.gamella@stat.math.ethz.ch) for such inquiries.

## Licenses

The resources to build the hardware, that is, the blueprints, schematics, component lists and the arduino and control code, are licensed under a [CC BY-NC-SA 4.0 license](https://creativecommons.org/licenses/by-nc-sa/4.0/).

