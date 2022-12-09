# KLE PCB Generator

This script makes it easier to create your own keyboard with fully custom key layout. It reads a file exported from the online [Keyboard Layout Editor](http://www.keyboard-layout-editor.com/) and generates a [KiCAD](https://www.kicad.org/) project from this, complete with schematic and layout. After manually finalizing the design you can generate the files a production service (such as [OSH Park](https://oshpark.com/) or [Eurocircuits](https://www.eurocircuits.com/)) needs to manufacture your PCB.

The generated schematic is pretty much complete and contains all key switches connected in rows and columns, a functional control circuit built around the ATmega32U4 (including external crystal, reset switch, programming header and a USB connector) and mounting holes. The layout is only partly routed, but contains all switches (including stabilizer mounting holes for keys that need it) in the correct position.

## Features

Current klepcbgen features are:

* Generate a project compatible with KiCad 5 and 6 (But check [this](./wiki/KiCad-6) first)
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

While this script takes care of a lot of the tedious and error-prone drudge-work (most notably correctly positioning all switches), the end-result is not a finished design you can immediately send off to be manufactured. There are a few manual steps required to get everything in working order:

1. Execute the script from the commandline, e.g. using the provided example layout as input: `python klepcbgen.py -o mykeyboard example_layout.json`
2. This generates a KiCad project in the subdirectory "mykeyboard"
3. Load the project in KiCad and double-click the kicad_pcb file to open it.
4. From the **Tools** menu, select **Update Footprints from Library...**
5. Make sure **Update all footprints on board** is the selected option, then click **Apply**. Once it finishes the update, click **Close**
6. From the **Tools** menu, select **Update PCB from Schematic...**
7. This will open the **Annotate** dialog for the schematic. Ensure **Keep existing annotations** is selected, then click **Annotate**
8. KiCad will automatically switch back to the **Update PCB from Schematic...** dialog once it finishes the annotation
9. Ensure the Match Method is set to **Re-associate footprints by reference** (for Kicad 5) or **Re-link footprints to schematic symbols based on their reference designators** (for Kicad 6). In both cases **THIS IS NOT THE DEFAULT**, so be sure to change it or it will mess up the switch placement. 
10. Click **Update PCB**

The schematic and pcb layout are now properly linked, although you will see a lot of unconnected traces. Automatically routing these connections is beyond the scope of this script, so the next step is finishing the board layout manually:

1. Check the board for problems. The script tries to partly route the key matrix. For this it applies some simple heuristics which give usable results in most cases. However, there's a good chance this simple approach leads to issues you'll need to fix, such as shorts or traces interfering with pads or through-holes. Use the Design Rule Checker (Inspect -> Design Rules Checker -> Run DRC). Disregard the unconnected items for now, but to check the "Problems/Markers" report.
2. Place the microcontroller circuit and USB connector. The best spot for these is highly board-specific and depends on personal preference.
3. Finish the key matrix layout. The script adds traces up to the boundary of each switch footprint. This **can** connect a switch to the next one in a column, but it often doesn't, so you'll have to make this connection yourself.
4. Connect the key-matrix and USB connector to the control circuit. This is the most time-consuming step as you will quickly run out of space in the area around the microcontroller.

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

* Smarter way to group keys in rows and columns, as the current approach does not allow for a full 104-key layout
* Support foorprints with stabilizers for vertical keys (numpad enter and 0)
* Add the option to use Alps footprints (Supported in KiCad as Matias switches)
* Support ISO-ENTER
* Support rotated keys

And further down the line:

* A board outline compatible with [swillkb's online Plate&Case Builder](http://builder.swillkb.com/).
* Lighting: obviously RGB is all the rage, so I would like to add options to generate a PCB which includes lighting
* Split layout: I'm a big fan of ergonomic/split layouts (I'm currently typing this on a Kinesis Freestyle Pro)
* Wireless: Cables are a nuisance.
* Multiple options for the control circuit: The ATmega32U4 is not the only option, and frankly doesn't have a lot of spare pins, e.g. for lighting

## License

 klepcbgen © 2020 by Jeroen Bouwens is licensed under CC BY-NC-SA 4.0. To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/