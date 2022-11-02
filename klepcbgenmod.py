"""Generate a KiCad project from a Keyboard Leyout Editor json input layout"""
import sys

import json
import datetime
import os
import math

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined

# Program version
PROGRAM_VERSION = "0.1"

# Constants
MAX_ROWS = 7
MAX_COLS = 18

class KeyBlockCollection:
    """Maintains a collection of blocks of keyboard keys, such as columns or rows"""
    def __init__(self):
        self.blocks = []

    def add_key_to_block(self, block_index, key_index):
        """Add a keyboard key to one of the blocks in the collection at the specified index.
           If the block does not exist, it gets created at the specified index, inserting a
           number of empty blocks if necessary"""
        # Check if the block exists, and add a number of blocks if needed
        blocks_to_add = (block_index + 1) - len(self.blocks)
        if blocks_to_add > 0:
            for _ in range(blocks_to_add):
                self.blocks.append([])

        self.blocks[block_index].append(key_index)

    def get_block(self, block_index):
        """Get the coimplete"""
        return self.blocks[block_index]


class Keyboard:
    """Represents an entire keyboard layout with all the keys positioned and
       grouped in rows and columns"""
    def __init__(self):
        self.keys = []
        self.rows = KeyBlockCollection()
        self.columns = KeyBlockCollection()
        self.name = ""
        self.author = ""

    def add_key_to_row(self, row_index, key_index):
        """Add a key to a specific row"""
        self.rows.add_key_to_block(row_index, key_index)

    def add_key_to_col(self, col_index, key_index):
        """Add a key to a specific column"""
        self.columns.add_key_to_block(col_index, key_index)

    def print_key_info(self):
        """ Print information for this keyboard """

        print("")
        print("Keyboard information: ")
        print("Name: " + self.name)
        print("Author: " + self.author)
        print(
            "Contains: "
            + str(len(self.keys))
            + " keys, grouped into "
            + str(len(self.rows.blocks))
            + " rows and "
            + str(len(self.columns.blocks))
            + " columns"
        )


class Key:
    """All required information about a single keyboard key"""
    x_unit = 0
    y_unit = 0
    width = 0
    height = 0
    row = 0
    col = 0
    rot = 0
    diodenetnum = 0
    colnetnum = 0
    rownetnum = 0
    num = 0
    legend = "<N/A>"


def unit_width_to_available_footprint(unit_width):
    """Convert a key width in standard keyboard units to the width of the kicad
       footprint to use"""
    if unit_width < 1.25:
        return "1.00"
    elif unit_width < 1.5:
        return "1.25"
    elif unit_width < 1.75:
        return "1.50"
    elif unit_width < 2:
        return "1.75"
    elif unit_width < 2.25:
        return "2.00"
    elif unit_width < 2.75:
        return "2.25"
    elif unit_width < 6.25:
        # This may not be the appropriate size for everything between 2.75 and
        # 6.25, but this is what we have
        return "2.75"

    # This may not be the appropriate size for everything >= 6.25, but this
    # is what we have
    return "6.25"

class Nets:
    """Maintains a collection of nets for use in the schematic"""
    def __init__(self):
        self.nets = []

    def number_of_nets(self):
        """Get the number of nets in the collection"""
        return len(self.nets)

    def add_net(self, net_name):
        """Add a net to the collection"""
        if not net_name in self.nets:
            self.nets.append(net_name)

        return self.get_net_num(net_name)

    def get_net_num(self, net_name):
        """Get the net number of the net with the specified name"""
        for index, name in enumerate(self.nets):
            if name == net_name:
                return index + 1

        return 0

    def get_net_name(self, index):
        """Get the name of the net with the specified net number"""
        if (index >= 0) and index < len(self.nets):
            return self.nets[index]
        else:
            return "UNKNOWN"

class KLEPCBGenerator:
    """Wrapper around the entire generator parses arguments, load json and generate kicad project"""
    keyboard = Keyboard()

    def __init__(self):
        """ Set-up directories """
        self.project_dir = Path(__file__).resolve().parent
        self.jinja_env = Environment(
            loader=FileSystemLoader([self.project_dir / "templates"]),
            undefined=StrictUndefined,
        )
        self.nets = Nets()

    def generate_kicadproject(self, infile, outname, do_routing, colgrouping):
        """Generate the kicad project. Main entry point"""

        if not os.path.exists(outname):
            os.mkdir(outname)

        self.read_kle_json(infile)
        self.generate_rows_and_columns(colgrouping)
        self.generate_schematic(outname)
        self.generate_layout(outname, do_routing)
        self.generate_project(outname)

    def read_kle_json(self, infile):
        """ Read the provided KLE input file and create a list of all the keyswitches that should
            be on the board """

        print("Reading input file '" + infile + "' ...")

        if infile == "-":
            kle_json = json.load(sys.stdin)
        else:
            with open(infile, "r", encoding="utf-8") as read_file:
                kle_json = json.load(read_file)

        # First create a list of switches, each with its own X,Y coordinate
        current_x = 0.0
        current_y = 0.0
        key_num = 0
        for row in kle_json:
            if isinstance(row, list):
                # Default keysize is 1x1
                key_width = 1
                key_height = 1
                # Extract all keys in a row
                for item in row:
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if key == "x":
                                current_x += value
                            elif key == "y":
                                current_y += value
                            elif key == "w":
                                key_width = value
                            elif key == "h":
                                key_height = value
                    elif isinstance(item, str):
                        new_key = Key()
                        new_key.num = key_num
                        new_key.x_unit = current_x + key_width / 2.0
                        new_key.y_unit = current_y + key_height / 2.0
                        if item == "":
                            new_key.legend = "Blank"
                        elif item == " ":
                            new_key.legend = "Space"
                        else:
                            new_key.legend = item

                        ## Perform some escaping on the legend text to satisfy KiCad
                        new_key.legend = new_key.legend.replace('\n', ",")
                        new_key.legend = new_key.legend.replace('~', '~~')
                        new_key.legend = new_key.legend.replace('\\', '\\\\')
                        new_key.legend = new_key.legend.replace('"', '\\\"')
                        
                        new_key.width = key_width
                        new_key.height = key_height
                        self.keyboard.keys.append(new_key)
                        current_x += key_width
                        key_num += 1
                        key_width = 1
                        key_height = 1
                    else:
                        print("Found unexpected JSON element (", item, "). Exiting")
                        exit()
                current_y += 1
                current_x = 0
            else:
                # Found the meta-info block.
                if "name" in row:
                    self.keyboard.name = row["name"]
                if "author" in row:
                    self.keyboard.author = row["author"]

    def generate_rows_and_columns(self, colgrouping):
        """ Group keys in rows and columns based on the position of the center of the switch in a
            grid """

        print("Grouping keys in rows and columns ... ")

        # For each key in the board, determine the Y of the center of the key. This determines
        # the row a key is in.
        keys_in_row = [0] * MAX_ROWS
        for index, key in enumerate(self.keyboard.keys):
            centery = key.y_unit-0.5
            row = math.floor(centery)
            if row > MAX_ROWS-1:
                exit("ERROR: Key placement produced too many rows. klepcbgen currently cannot generate a valid KiCad project for this keyboard layout.\nExiting ...")

            self.keyboard.add_key_to_row(row, index)
            self.keyboard.keys[index].row = row

            keys_in_row[row] += 1

            if keys_in_row[row] > MAX_COLS-1:
                exit("ERROR: Key placement produced too many columns. klepcbgen currently cannot generate a valid KiCad project for this keyboard layout.\nExiting ...")

        # Sort the keys in each row by X-coordinate, then assign a column to each key
        for row in self.keyboard.rows.blocks:
            row.sort(key=lambda key_index: self.keyboard.keys[key_index].x_unit)

            col = 0
            for key_index in row:
                key = self.keyboard.keys[key_index]

                # Determine the column based on x-coordinate instead of sequentially
                if colgrouping == 'pos':
                    centerx = key.x_unit-0.5
                    col = math.floor(centerx)

                self.keyboard.add_key_to_col(col, key_index)
                key.col = col
                col += 1
                
    def place_schematic_components(self):
        """Place schematic components determined by the layout(keyswitches and diodes)"""
        switch_tpl = self.jinja_env.get_template("schematic/keyswitch.tpl")

        component_count = 0
        components_section = ""

        # Place keyswitches and diodes
        for key in self.keyboard.keys:
            placement_x = int(600 + key.x_unit * 800)
            placement_y = int(800 + key.y_unit * 500)

            components_section = components_section + switch_tpl.render(
                num=component_count,
                legend=key.legend,
                x=placement_x,
                y=placement_y,
                rowNum=key.row,
                colNum=key.col,
                keywidth=unit_width_to_available_footprint(key.width),
            )
            components_section = components_section + "\n"
            component_count += 1

        return components_section

    def generate_schematic(self, outname):
        """ Generate schematic """

        print("Generating schematic ...")

        components = self.place_schematic_components()
        control_circuit = self.jinja_env.get_template("schematic/controlcircuit.tpl")
        schematic = self.jinja_env.get_template("schematic/schematic.tpl")
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        comment = (
            "Generated by " + os.path.basename(sys.argv[0]) + " v" + PROGRAM_VERSION
        )
        with open(
                outname + "/" + os.path.basename(os.path.normpath(outname)) + ".sch", "w+", newline="\n", encoding="utf-8"
        ) as out_file:
            out_file.write(
                schematic.render(
                    components=components,
                    controlcircuit=control_circuit.render(),
                    title=self.keyboard.name,
                    author=self.keyboard.author,
                    date=now,
                    comment=comment,
                )
            )

    def place_layout_components(self, do_routing):
        """ Place footprint components, traces and vias """
        switch = self.jinja_env.get_template("layout/keyswitch.tpl")
        diode = self.jinja_env.get_template("layout/diode.tpl")
        component_count = 0
        components_section = ""

        # Load templates for netnames
        diodetpl = self.jinja_env.get_template("layout/diodenetname.tpl")
        rowtpl = self.jinja_env.get_template("layout/rownetname.tpl")
        coltpl = self.jinja_env.get_template("layout/colnetname.tpl")
        tracetpl = self.jinja_env.get_template("layout/trace.tpl")

        # Place keyswitches, diodes, vias and traces
        key_pitch = 19.05
        key_origin_x = -100
        key_origin_y = 17.78

        # diode_offset = [-6.35, 8.89]
        # col_via_offsets = [[0, -2.03], [0, 12.24]]
        # row_via_offsets = [[-9.68, 9.83], [4.6, 9.83]]
        # diode_trace_offsets = [[-6.38, 2.54], [-6.38, 7.77]]

        # Several offsets that are relative to the 0,0 poin inside the switch layout template
        diode_offset = [-5.8, 8.89]                         # Position of the diode 
        diode_trace_offsets = [[-5.8, 2.54], [-5.8, 7.77]]  # Start/end-points for the trace connecting the diode to the switch
        row_trace_offset = [-5.8, 9.83]     # Position of the bottom pad of the diode
        switch_contact_x_offset = 0.55      # Small offset for the vertical traces to avoid them getting too close to pads
        switch_corner_y = 10                # Y-offset of the point where the downward trace can angle towards the next switch
        switch_top = -4.50                  # Y-offset for the top of the Dwgs rectangle in the switch template
        switch_bottom = 14.5                # Y-offset for the bottom of the Dwgs rectangle in the switch template
        switch_left = -12                   # X-offset for the left of the Dwgs rectangle in the switch template
        switch_right = 7                    # X-offset for the right of the Dwgs rectangle in the switch template

        for key in self.keyboard.keys:
            # Place switch
            ref_x = key_origin_x + key.x_unit * key_pitch
            ref_y = key_origin_y + key.y_unit * key_pitch
            components_section = (
                components_section
                + switch.render(
                    num=component_count,
                    legend=key.legend,
                    x=ref_x,
                    y=ref_y,
                    diodenetnum=key.diodenetnum,
                    diodenetname=diodetpl.render(diodenum=key.num),
                    colnetnum=key.colnetnum,
                    colnetname=coltpl.render(colnum=key.col),
                    keywidth=unit_width_to_available_footprint(key.width),
                )
                + "\n"
            )
            # Place diode
            diode_x = ref_x + diode_offset[0]
            diode_y = ref_y + diode_offset[1]
            components_section = (
                components_section
                + diode.render(
                    num=component_count,
                    x=diode_x,
                    y=diode_y,
                    diodenetnum=key.diodenetnum,
                    diodenetname=diodetpl.render(diodenum=key.num),
                    rownetnum=key.rownetnum,
                    rownetname=rowtpl.render(rownum=key.row),
                )
                + "\n"
            )

            # Connect diode to switch
            components_section = (
                components_section
                + tracetpl.render(
                    x1=ref_x + diode_trace_offsets[0][0],
                    y1=ref_y + diode_trace_offsets[0][1],
                    x2=ref_x + diode_trace_offsets[1][0],
                    y2=ref_y + diode_trace_offsets[1][1],
                    layer="B.Cu",
                    netnum=key.diodenetnum,
                )
                + "\n"
            )

            component_count += 1

        if do_routing:
            # Add traces between all diodes in a row
            for row in self.keyboard.rows.blocks:
                prev_index = -1
                for key_index in row:
                    if(prev_index != -1):                    
                        left_key = self.keyboard.keys[prev_index]
                        right_key = self.keyboard.keys[key_index]

                        left_diode_x = key_origin_x + left_key.x_unit * key_pitch + row_trace_offset[0]
                        left_diode_y = key_origin_y + left_key.y_unit * key_pitch + row_trace_offset[1]

                        right_diode_x = key_origin_x + right_key.x_unit * key_pitch + row_trace_offset[0]
                        right_diode_y = key_origin_y + right_key.y_unit * key_pitch + row_trace_offset[1]

                        components_section = (
                            components_section
                            + tracetpl.render(
                                x1=left_diode_x,
                                y1=left_diode_y,
                                x2=right_diode_x,
                                y2=right_diode_y,
                                layer="B.Cu",
                                netnum=left_key.rownetnum,
                            )
                            + "\n"
                        )
                    prev_index = key_index

            # Add (partial) traces between switches columns
            for column in self.keyboard.columns.blocks:
                prev_index = -1
                for key_index in column:
                    if(prev_index != -1):                    
                        top_key = self.keyboard.keys[prev_index]
                        bot_key = self.keyboard.keys[key_index]

                        top_hole_x = key_origin_x + top_key.x_unit * key_pitch
                        top_hole_y = key_origin_y + top_key.y_unit * key_pitch

                        bot_hole_x = key_origin_x + bot_key.x_unit * key_pitch
                        bot_hole_y = key_origin_y + bot_key.y_unit * key_pitch

                        components_section = (
                            components_section
                            + tracetpl.render(
                                x1=top_hole_x + switch_contact_x_offset,
                                y1=top_hole_y,
                                x2=top_hole_x + switch_contact_x_offset,
                                y2=top_hole_y + switch_corner_y,
                                layer="F.Cu",
                                netnum=top_key.colnetnum,
                            )
                            + "\n"
                        )

                        to_x = top_hole_x + switch_contact_x_offset
                        if to_x > bot_hole_x + switch_right:
                            to_x = bot_hole_x + switch_right
                        elif to_x < bot_hole_x + switch_left:
                            to_x = bot_hole_x + switch_left

                        components_section = (
                            components_section
                            + tracetpl.render(
                                x1=bot_hole_x + switch_contact_x_offset,
                                y1=bot_hole_y,
                                x2=to_x,
                                y2=bot_hole_y + switch_top,
                                layer="F.Cu",
                                netnum=top_key.colnetnum,
                            )
                            + "\n"
                        )

                        if to_x > top_hole_x + switch_right:
                            to_x = top_hole_x + switch_right
                        elif to_x < top_hole_x + switch_left:
                            to_x = top_hole_x + switch_left

                        components_section = (
                            components_section
                            + tracetpl.render(
                                x1=top_hole_x + switch_contact_x_offset,
                                y1=top_hole_y + switch_corner_y,
                                x2=to_x,
                                y2=top_hole_y + switch_bottom,
                                layer="F.Cu",
                                netnum=top_key.colnetnum,
                            )
                            + "\n"
                        )

                    prev_index = key_index


        return components_section, component_count

    def define_nets(self):
        """Define all the nets for this layout"""
        self.nets.add_net("GND")
        self.nets.add_net("VCC")
        self.nets.add_net('"Net-(C6-Pad1)"')
        self.nets.add_net('"Net-(C7-Pad1)"')
        self.nets.add_net('"Net-(C8-Pad1)"')
        self.nets.add_net('"Net-(J1-Pad4)"')
        self.nets.add_net('"Net-(J1-Pad3)"')
        self.nets.add_net('"Net-(J1-Pad2)"')
        self.nets.add_net('"Net-(R1-Pad1)"')
        self.nets.add_net('"Net-(R2-Pad1)"')
        self.nets.add_net('"Net-(R3-Pad1)"')
        self.nets.add_net('"Net-(R4-Pad2)"')
        self.nets.add_net('"Net-(U1-Pad42)"')
        self.nets.add_net('/Reset')

        row_tpl = self.jinja_env.get_template("layout/rownetname.tpl")
        # Always declare the max number of row nets, since the control circuit template refers to them
        for row_num in range(MAX_ROWS):
            self.nets.add_net(row_tpl.render(rownum=row_num))

        col_tpl = self.jinja_env.get_template("layout/colnetname.tpl")
        # Always declare the max number of column nets, since the control circuit template refers to them
        for col_num in range(MAX_COLS): 
            self.nets.add_net(col_tpl.render(colnum=col_num))

        diode_tpl = self.jinja_env.get_template("layout/diodenetname.tpl")
        for diode_num in range(len(self.keyboard.keys)):
            self.nets.add_net(diode_tpl.render(diodenum=diode_num))

    def create_layout_nets(self):
        """ Create the list of nets in the layout """
        addnets = ""
        declarenets = ""

        # Create a declaration and addition for each net
        for netnum in range(0, 1 + self.nets.number_of_nets()):
            netname = self.nets.get_net_name(netnum)
            declarenets = (
                declarenets + "  (net " + str(netnum + 1) + " " + netname + ")\n"
            )
            addnets = addnets + "    (add_net " + netname + ")\n"

        # make each key in the board aware in which row/column/diode net it resides
        rowtpl = self.jinja_env.get_template("layout/rownetname.tpl")
        for index, row in enumerate(self.keyboard.rows.blocks):
            rownetname = rowtpl.render(rownum=index)
            for keyindex in row:
                self.keyboard.keys[keyindex].rownetnum = self.nets.get_net_num(
                    rownetname
                )

        coltpl = self.jinja_env.get_template("layout/colnetname.tpl")
        for index, col in enumerate(self.keyboard.columns.blocks):
            colnetname = coltpl.render(colnum=index)
            for keyindex in col:
                self.keyboard.keys[keyindex].colnetnum = self.nets.get_net_num(
                    colnetname
                )

        diodetpl = self.jinja_env.get_template("layout/diodenetname.tpl")
        for diodenum in range(len(self.keyboard.keys)):
            diodenetname = diodetpl.render(diodenum=diodenum)
            self.keyboard.keys[diodenum].diodenetnum = self.nets.get_net_num(
                diodenetname
            )

        nets = self.jinja_env.get_template("layout/nets.tpl")

        return nets.render(netdeclarations=declarenets, addnets=addnets)

    def generate_layout(self, outname, do_routing):
        """ Generate layout """

        print("Generating PCB layout ...")

        self.define_nets()
        nets = self.create_layout_nets()

        components, numcomponents = self.place_layout_components(do_routing)

        layout = self.jinja_env.get_template("layout/layout.tpl")
        controlcircuit = self.jinja_env.get_template("layout/controlcircuit.tpl")
        layout_output_file_path = outname + "/" + os.path.basename(os.path.normpath(outname)) + ".kicad_pcb"
        with open(layout_output_file_path, "w+", newline="\n", encoding="utf-8") as out_file:
            out_file.write(
                layout.render(
                    modules=components,
                    nummodules=numcomponents,
                    nets=nets,
                    numnets=self.nets.number_of_nets(),
                    controlcircuit=controlcircuit.render(nets=self.nets, startnet=0),
                )
            )

    def generate_project(self, outname):
        """Generate the project file"""
        prj = self.jinja_env.get_template("kicadproject.tpl")
        with open(
                outname + "/" + os.path.basename(os.path.normpath(outname)) + ".pro", "w+", newline="\n", encoding="utf-8"
        ) as out_file:
            out_file.write(prj.render())

