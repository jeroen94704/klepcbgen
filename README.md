# KLE PCB Generator

This script makes it easier to create your own keyboard with fully custom key layout. It reads a file exported from the online [Keyboard Layout Editor](http://www.keyboard-layout-editor.com/) and generates a [KiCAD](https://www.kicad.org/) project from this, complete with schematic and layout. After manually finalizing the design you can generate the files a production service (such as [OSH Park](https://oshpark.com/) or [Eurocircuits](https://www.eurocircuits.com/)) needs to manufacture your PCB.

The generated schematic is pretty much complete and contains all key switches connected in rows and columns, a functional control circuit built around the ATmega32U4 (including external crystal, reset switch, programming header and a USB connector) and mounting holes. The layout is only partly routed, but contains all switches (including stabilizer mounting holes for keys that need it) in the correct position.

## Features

Current klepcbgen features are:

* Generate a project compatible with KiCad 5 and 6 (But check [this](../../wiki/KiCad-6) first)
* Use only standard KiCad libraries
* Keys of different widths and/or heights
* Add stabilizers to keys 2 units or more wide
* Cherry MX switch mount
* Limitation: layouts with at most 18 columns and 7 rows

Currently **not** supported are:

* Keys with secondary width/height (So no ISO ENTER keys for now, sorry!)
* Rotated keys
* Vertical keys (e.g. numpad ENTER and "+")
* Alps switches

## Installation

Start by [downloading and unzipping the code](https://github.com/jeroen94704/klepcbgen/archive/master.zip) or by cloning the repository:

`git clone https://github.com/jeroen94704/klepcbgen`

Then install the required dependencies, using the following command:

`pip install -r requirements.txt`

(Note: On Windows, make sure to execute this command in a shell with admin rights)

## Usage

Please read [this wiki page](../../wiki/Usage) for usage instructions.

## Kicad 6

Additional instructions regarding Kicad 6 can be found [here](../../wiki/KiCad-6).

## Future improvements

Core features:

* Smarter options for rows/columns grouping, as the current approach does not allow for a full 104-key layout
* Support foorprints with stabilizers for vertical keys (numpad enter and 0)
* Add the option to use Alps footprints (Supported in KiCad as Matias switches)
* Support ISO-ENTER
* Support rotated keys

More advanced options:

* A board outline compatible with [swillkb's online Plate&Case Builder](http://builder.swillkb.com/).
* Support for easy generation of keyboard firmware.
* Lighting: obviously RGB is all the rage, so I would like to add options to generate a PCB which includes lighting
* Split layout: I'm a big fan of ergonomic/split layouts (I'm currently typing this on a Kinesis Freestyle Pro)
* Wireless: Becaue cables are a nuisance.
* Alternative control circuits: The ATmega32U4 is not the only option, and frankly doesn't have a lot of spare pins, e.g. for lighting

## Donate

If you find this project useful a small donation is much appreciated (but by no means required or expected): https://ko-fi.com/jeroen94704

## License

 klepcbgen © 2020 by Jeroen Bouwens is licensed under CC BY-NC-SA 4.0. To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
