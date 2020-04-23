# KLE PCB Generator

This script takes a json file exported from the online [Keyboard Layout Editor](http://www.keyboard-layout-editor.com/) and generates a KiCAD schematic and layout out of this. The resulting schematic is pretty much complete: it contains all key switches connected in rows and columns, a functional control circuit built around the ATmega32U4 (including external crystal, reset switch and a USB connector) and mounting holes. The layout is only partly connected, but most crucially it contains all switches in the right positions (including holes for stabilizers for keys that need it).

# Features

At this point klepcbgen supports only the bare minimum of features:

* Keys of different widths and/or heights
* Stabilizers for keys 2 units or more wide
* Cherry MX switch mount
* Does not require custom KiCad libraries

Features available in KLE that would impact a PCB but are currently **not** supported are:

* Secondary width/height (So no ISO/big-ass ENTER keys for now, sorry!)
* Rotated keys
* Alps switch mount
* Plate mounted switches (although I think the footprints for PCB mounted switches are compatible with plate mounted switches)

# Manual

While this script takes care of a lot of the tedious drudge-work (most notably correctly positioning all switches), the end-result is not a finished layout you can immediately send off to be manufactured. There are a few manual steps required to get everything in working order:

* Execute the script from the commandline: `python klepcbgen.py example_layout.json mykeyboard`
* This generates the KiCad project in the subdirectory "mykeyboard"
* Load the project in KiCad and double-click the kicad_pcb file to open it.
* From the **Tools** menu, select **Update Footprints from Library...**
* Make sure **Update all footprints on board** is the selected option, then click **Apply**. Once it finishes the update, click **Close**
* From the **Tools** menu, select **Update PCB from Schematic...**
* This will open the **Annotate** dialog for the schematic. Ensure **Keep existing annotations** is selected, then click **Annotate**
* KiCad will automatically switch back to the **Update PCB from Schematic...** dialog once it finishes the annotation
* Ensure the Match Method is set to **Re-associate footprints by reference** (**THIS IS NOT THE DEFAULT, SO BE SURE TO CHANGE IT**) and click **Update PCB**

The schematic and pcb layout are now properly linked. You will see a lot of unconnected traces. Automatically routing these connections is beyond the scope of this script, so you will have to do this manually. Also, the microcontroller circuit and USB connector are placed outside the board outline. The best placement for these is highly board-specific, and even depends on your preference, so this has to be done manually as well.

Once you finish the PCB, you can generate the set of Gerber files 

# Future improvements

I have a bunch of ideas for this generator, such as:

* A board outline compatible with [swillkb's online Plate&Case Builder](http://builder.swillkb.com/). 
* Lighting: obviously RGB is all the rage, so I would like to add options to generate a PCB which includes lighting
* Split layout: I'm a big fan of ergonomic/split layouts (I'm currently typing this on a Kinesis Freestyle Pro)
* Wireless: Cables are a nuisance.
* Multiple options for the control circuit: The ATmega32U4 is not the only option, and frankly doesn't have a lot of spare pins, e.g. for lighting

As you can guess, I'd love to make my own split, wireless, RGB-lit keyboard.


