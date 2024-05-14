# Building the Chambers

Here you can find the resources to build the wind tunnel and light tunnel described in the original [paper](https://arxiv.org/pdf/2404.11341.pdf). In particular,

- [`blueprints/`](blueprints/) contains the laser cutter designs for the framework and enclosures of the chambers.
- [`electronics/`](blueprints/) contains the diagrams for the electronic components of the chambers.
- [`component_list.md`](component_list.md) contains a list of all necessary components to build each chamber, including all the sensors and the camera.
- [`arduino/`](arduino/) contains the code that runs on the control computers aboard the chambers, including all necessary libraries.
- [`control/`](control/) contains the Python application to send commands and receive data from the chambers.
- [`datasheets/`](datasheets/) contains the datasheets for all components, outlined in appendix VI of the original [paper](https://arxiv.org/pdf/2404.11341.pdf).

**Note**: We are still working on the blueprints, electronics diagrams and component lists for the latest version of the chambers. Please check again soon or shoot us (Juan) an email!

## Disclaimer

To build the chambers you will need some common assembly tools and access to some more specialized equipment: a laser cutter of sufficient size (we used the [Trotec Speedy 400](https://www.troteclaser.com/de-ch/lasermaschinen/lasergravurmaschine-speedy)) and an electronics bench (for soldering and testing). We assume that you already posses the pertinent knowledge to use them.

If you would like to build the chambers but you lack the necessary skills or equipment, there is a *chance* we can build them for you or find an alternative solution. Please reach out to [Juan L. Gamella](mailto:juan.gamella@stat.math.ethz.ch) for inquiries.

## Licenses

The blueprints and diagrams are licensed under a [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/). A copy of the license can be found in [LICENSE_HARDWARE.txt](LICENSE_HARDWARE.txt).

The code under `arduino/` and `control/` is shared under the [MIT license](https://opensource.org/license/mit/). A copy of the license can also be found in [LICENSE_SOFTWARE.txt](LICENSE_SOFTWARE.txt).
