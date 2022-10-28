# KLE PCB Generator

This script takes a json file exported from the online [Keyboard Layout Editor](http://www.keyboard-layout-editor.com/) and generates a KiCAD schematic and layout out of this. The resulting schematic is pretty much complete: it contains all key switches connected in rows and columns, a functional control circuit built around the ATmega32U4 (including external crystal, reset switch, programming header and a USB connector) and mounting holes. The layout is only partly connected, but most crucially it contains all switches in the right positions (including holes for stabilizers for keys that need it).

## Features

Current klepcbgen features are:

* Keys of different widths and/or heights
* Adds stabilizers for keys 2 units or more wide
* Cherry MX switch mount
* Keyboard layouts with at most 18 columns and 7 rows
* Uses only standard KiCad libraries

Currently **not** supported are:

* Keys with secondary width/height (So no ISO/big-ass ENTER keys for now, sorry!)
* Rotated keys
* Vertical keys (e.g. numpad ENTER and "+")
* Alps switches

## Installation

klepcbgen requires python 3 and the jinja2 template module. Assuming you have a reasonably recent python install which includes pip by default, you can simply install jinja2 using the following command:

`pip install jinja2`

(Note: On Windows, make sure to execute this command in a shell with admin rights)

Then either [download and unzip the code](https://github.com/jeroen94704/klepcbgen/archive/master.zip) or clone the repository:

`git clone https://github.com/jeroen94704/klepcbgen`

## Usage

While this script takes care of a lot of the tedious and error-prone drudge-work (most notably correctly positioning all switches), the end-result is not a finished layout you can immediately send off to be manufactured. There are a few manual steps required to get everything in working order:

1. Execute the script from the commandline, e.g. using the provided example layout as input: `python klepcbgen.py example_layout.json mykeyboard`
2. This generates a KiCad project in the subdirectory "mykeyboard"
3. Load the project in KiCad and double-click the kicad_pcb file to open it.
4. From the **Tools** menu, select **Update Footprints from Library...**
5. Make sure **Update all footprints on board** is the selected option, then click **Apply**. Once it finishes the update, click **Close**
6. From the **Tools** menu, select **Update PCB from Schematic...**
7. This will open the **Annotate** dialog for the schematic. Ensure **Keep existing annotations** is selected, then click **Annotate**
8. KiCad will automatically switch back to the **Update PCB from Schematic...** dialog once it finishes the annotation
9. Ensure the Match Method is set to **Re-associate footprints by reference** (**THIS IS NOT THE DEFAULT, SO BE SURE TO CHANGE IT**) and click **Update PCB**

The schematic and pcb layout are now properly linked. You will see a lot of unconnected traces. Automatically routing these connections is beyond the scope of this script, so you will have to do this manually. Also, the microcontroller circuit and USB connector are placed outside the board outline. The best placement for these is highly board-specific, and even depends on your preference, so this has to be done manually as well.

Once you finish the PCB, you can generate the set of Gerber files, as explained for example [in this guide](https://github.com/ruiqimao/keyboard-pcb-guide).

## Kicad 6

klepcbgen generates files in kicad 5 format. Fortunately, kicad 6 is able to read these files and save them in the new format. Unfortunately, some of the footprints changed between 5 and 6 which results in a number of error when updating the footprints (step 5 above). For now you'll have to change these  manually. In particular, you need to change the footprints for the SMD capacitors and resistors.

To do this, perform the following steps:

1. Hover on the outline of one of the C's and press "e" to open the properties (if you hover on e.g. a pad it'll open the wrong dialog)
2. Click "Change Footprint..."
3. Select the option "Change footprints with library id:" (leave the id unchanged)
4. Change the "New footprint library id" to **Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder**
5. Click "Change"

Repeat these steps for the resistors, changing their footprint library id to **Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder**

Also note that the Match Method mentioned in step 9 above is called "Re-link footprints to schematic symbols based on their reference designators" in kicad 6.

## Future improvements

* Smarter way to group keys in rows and columns, as the current approach does not even allow for a full 104-key layout
* Support foorprints with stabilizers for vertical keys (numpad enter and 0)
* Add the option to use Alps footprints (Supported in KiCad as Matias switches)
* Support ISO-ENTER
* Support rotated keys

I also have a bunch of ideas for this generator, such as:

* A board outline compatible with [swillkb's online Plate&Case Builder](http://builder.swillkb.com/).
* Lighting: obviously RGB is all the rage, so I would like to add options to generate a PCB which includes lighting
* Split layout: I'm a big fan of ergonomic/split layouts (I'm currently typing this on a Kinesis Freestyle Pro)
* Wireless: Cables are a nuisance.
* Multiple options for the control circuit: The ATmega32U4 is not the only option, and frankly doesn't have a lot of spare pins, e.g. for lighting

As you can guess, I'd love to make my own split, wireless, RGB-lit keyboard.
