import json
import argparse
import datetime
import sys
import os
import math
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from pathlib import Path

# Program version
PROGRAM_VERSION='0.1'

class KeyBlockCollection:
    def __init__(self):
        self.blocks = []

    def addKeyToBlock(self, blockIndex, keyIndex):
        # Check if the block exists, and add a number of blocks if needed
        blocksToAdd = (blockIndex+1) - len(self.blocks) 
        if blocksToAdd > 0:
            for index in range(blocksToAdd):
                self.blocks.append([])
        
        self.blocks[blockIndex].append(keyIndex)

    def getBlock(self, blockIndex):
        return self.blocks[blockIndex]


class Keyboard:
    def __init__(self):
        self.keys = []
        self.rows = KeyBlockCollection()
        self.columns = KeyBlockCollection()
        self.name = ""
        self.author = ""

    def addKeyToRow(self, rowIndex, keyIndex):
        self.rows.addKeyToBlock(rowIndex, keyIndex)

    def addKeyToCol(self, colIndex, keyIndex):
        self.columns.addKeyToBlock(colIndex, keyIndex)

    def printKeyInfo(self):
        """ Print information for this keyboard """

        print("")
        print("Keyboard information: ")
        print("Name: " + self.name)
        print("Author: " + self.author)
        print("Contains: " + str(len(self.keys)) + " keys, grouped into " + str(len(self.rows.blocks)) + " rows and " + str(len(self.columns.blocks)) + " columns")

class Key:
    x = 0
    y = 0
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

def unitWidthToAvailableFootprint(unitwidth):
    if unitwidth < 1.25:
        return "1.00"
    elif unitwidth < 1.5:
        return "1.25"
    elif unitwidth < 1.75:
        return "1.50"
    elif unitwidth < 2:
        return "1.75"
    elif unitwidth < 2.25:
        return "2.00"
    elif unitwidth < 2.75:
        return "2.25"
    elif unitwidth < 6.25: 
        return "2.75" # This may not be the appropriate size for everything between 2.75 and 6.25, but this is what we have
    else:
        return "6.25" # This may not be the appropriate size for everything >= 6.25, but this is what we have

class KLEPCBGenerator:
    keyboard = Keyboard()

    """ Set-up directories """
    def __init__(self):
        self.project_dir = Path(__file__).resolve().parent
        self.jinja_env = Environment(
            loader = FileSystemLoader([self.project_dir / 'templates']),
            undefined = StrictUndefined
            )

    def generate_kicadproject(self):
        arguments = self.parse_command_line_arguments()

        if not os.path.exists('./' + arguments.outname):
            os.mkdir('./' + arguments.outname)

        self.read_kle_json(arguments)
        self.generate_rows_and_columns()
        self.generate_schematic(arguments)
        self.generate_layout(arguments)
        self.generate_project(arguments)

    def parse_command_line_arguments(self):
        """ Parse the command line and check that the correct number of arguments is given """
        parser = argparse.ArgumentParser(prog='klepcbgen', description = 'Utility to generate a KiCad schematic and layout of the switch matrix of a keyboard designed using the Keyboard Layout Editor (http://www.keyboard-layout-editor.com/)')
        parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + PROGRAM_VERSION)
        parser.add_argument('infile', help='A JSON file containing a keyboard layout in the KLE JSON format')
        parser.add_argument('outname', help='The base name of the output files (e.g. "id80" will result in "id80.sch" and "id80.pcb"')
        args = parser.parse_args()

        if not args.infile:
            print('')
            parser.error("Not all required arguments are present. Use the options '-h' for more information")

        return args

    def read_kle_json(self, args):
        """ Read the provided KLE input file and create a list of all the keyswitches that should be on the board """

        print("Reading input file '" + args.infile + "' ...")

        with open(args.infile, "r", encoding="latin-1") as read_file:
            kleJSON = json.load(read_file)

        # First create a list of switches, each with its own X,Y coordinate
        x=0.0
        y=0.0
        keyNum = 0
        for row in kleJSON:
            if isinstance(row, list):
                # Default keysize is 1x1
                keyWidth = 1
                keyHeight = 1
                # Extract all keys in a row
                for item in row:
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if key == 'x':
                                x += value
                            elif key == 'y':
                                y += value
                            elif key == 'w':
                                keyWidth = value
                            elif key == 'h':
                                keyHeight = value
                    elif isinstance(item, str):
                        k = Key()
                        k.num = keyNum
                        k.x = x + keyWidth / 2
                        k.y = y + keyHeight / 2
                        k.legend = item
                        k.width = keyWidth
                        k.height = keyHeight
                        self.keyboard.keys.append(k)

                        x += keyWidth
                        keyNum += 1
                        keyWidth = 1
                        keyHeight = 1
                    else:
                        print("Found unexpected JSON element (", item, "). Exiting")
                        exit()
                y += 1
                x = 0
            else:
                # Found the meta-info block.
                if 'name' in row:
                    self.keyboard.name = row['name']
                if 'author' in row:
                    self.keyboard.author = row['author']


    def generate_rows_and_columns(self):
        """ Group keys in rows and columns based on the position of the center of the switch in a grid """

        print("Grouping keys in rows and columns ... ")

        # For each key in the board, determine the X,Y of the center of the key. This determines the row/column a key is in
        for index, key in enumerate(self.keyboard.keys):
            centerx = key.x
            col = math.floor(centerx)
            self.keyboard.addKeyToCol(col, index)
            self.keyboard.keys[index].col = col

            centery = key.y
            row = math.floor(centery)
            self.keyboard.addKeyToRow(row, index)
            self.keyboard.keys[index].row = row

    def place_schematic_components(self):
        switchTpl = self.jinja_env.get_template('schematic/keyswitch.tpl')

        componentCount = 0
        componentsSection = ""

        # Place keyswitches and diodes
        for key in self.keyboard.keys:
            placementX = int(600 + key.x * 800)
            placementY = int(800 + key.y * 500)
            
            componentsSection = componentsSection + switchTpl.render(num=componentCount, x=placementX, y=placementY, rowNum = key.row, colNum = key.col, 
                                                                     keywidth = unitWidthToAvailableFootprint(key.width))
            componentsSection = componentsSection + "\n"
            componentCount += 1

        return componentsSection

    def generate_schematic(self, args):
        """ Generate schematic """

        print("Generating schematic ...")

        components = self.place_schematic_components()
        schematic = self.jinja_env.get_template('schematic/schematic.tpl')
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        comment = 'Generated by ' + os.path.basename(sys.argv[0]) + ' v' + PROGRAM_VERSION
        with open(args.outname + '/' + args.outname + '.sch', 'w', newline='\n') as out_file:
            out_file.write(schematic.render(components=components, title=self.keyboard.name, author=self.keyboard.author, date=now, comment=comment))

    def place_layout_components(self):
        """ Place footprint components, traces and vias """
        switch = self.jinja_env.get_template('layout/keyswitch.tpl')
        diode = self.jinja_env.get_template('layout/diode.tpl')
        componentCount = 0
        componentsSection = ""

        # Load templates for netnames
        diodetpl = self.jinja_env.get_template("layout/diodenetname.tpl")
        rowtpl = self.jinja_env.get_template("layout/rownetname.tpl")
        coltpl = self.jinja_env.get_template("layout/colnetname.tpl")
        viatpl = self.jinja_env.get_template("layout/via.tpl")
        tracetpl = self.jinja_env.get_template("layout/trace.tpl")

        # Place keyswitches, diodes, vias and traces
        keyPitch = 19.05
        diodeOffset = [-6.35, 8.89]
        colViaOffsets = [[0,-2.03], [0, 12.24]]
        rowViaOffsets = [[-9.68,9.83], [4.6,9.83]]
        diodeTraceOffsets = [[-6.38, 2.54], [-6.38, 7.77]]

        for key in self.keyboard.keys:
            # Place switch
            refX = 25.4 + key.x * keyPitch
            refY = 17.78 + key.y * keyPitch
            componentsSection = componentsSection + switch.render(num=componentCount, x=refX, y=refY,
                                    diodenetnum=key.diodenetnum, 
                                    diodenetname=diodetpl.render(diodenum = key.num) , 
                                    colnetnum=key.colnetnum, 
                                    colnetname=coltpl.render(colnum = key.col),
                                    keywidth = unitWidthToAvailableFootprint(key.width)) + "\n"
            # Place diode
            diodeX = refX + diodeOffset[0]
            diodeY = refY + diodeOffset[1]
            componentsSection = componentsSection + diode.render(num=componentCount, x=diodeX, y=diodeY,
                                    diodenetnum=key.diodenetnum, 
                                    diodenetname=diodetpl.render(diodenum = key.num) , 
                                    rownetnum=key.rownetnum, 
                                    rownetname=rowtpl.render(rownum = key.row)) + "\n"

            # Place vias
            for offset in colViaOffsets:
                viaX = refX + offset[0]
                viaY = refY + offset[1]
                componentsSection = componentsSection + viatpl.render(x=viaX, y=viaY, netnum=key.colnetnum) + "\n"

            for offset in rowViaOffsets:
                viaX = refX + offset[0]
                viaY = refY + offset[1]
                componentsSection = componentsSection + viatpl.render(x=viaX, y=viaY, netnum=key.rownetnum) + "\n"

            # Place traces
            componentsSection = componentsSection + tracetpl.render(x1=refX+rowViaOffsets[0][0], y1=refY+rowViaOffsets[0][1], 
                                                                  x2=refX+rowViaOffsets[1][0], y2=refY+rowViaOffsets[1][1], 
                                                                  layer="B.Cu", netnum=key.rownetnum) + "\n"

            componentsSection = componentsSection + tracetpl.render(x1=refX+colViaOffsets[0][0], y1=refY+colViaOffsets[0][1], 
                                                                  x2=refX+colViaOffsets[1][0], y2=refY+colViaOffsets[1][1], 
                                                                  layer="F.Cu", netnum=key.colnetnum) + "\n"

            componentsSection = componentsSection + tracetpl.render(x1=refX+diodeTraceOffsets[0][0], y1=refY+diodeTraceOffsets[0][1], 
                                                                  x2=refX+diodeTraceOffsets[1][0], y2=refY+diodeTraceOffsets[1][1], 
                                                                  layer="B.Cu", netnum=key.diodenetnum) + "\n"

            # Place stabilizer mount holes, if necessary
            
                                                       
            componentCount += 1

        return componentsSection, componentCount


    def define_nets(self):
        """ Create the list of nets in the layout """
        netnum = 1
        addnets = ""
        # Create a net for each row ...
        rownets = ""
        rowtpl = self.jinja_env.get_template("layout/rownetname.tpl")
        for rownum, row in enumerate(self.keyboard.rows.blocks):
            netname = rowtpl.render(rownum = rownum)
            rownets = rownets + "  (net " + str(netnum) + " " + netname + ")\n"
            addnets = addnets + "    (add_net " + netname + ")\n"
            for keyindex in row:
                self.keyboard.keys[keyindex].rownetnum = netnum
            netnum += 1

        # ... and for each column
        colnets = ""
        coltpl = self.jinja_env.get_template("layout/colnetname.tpl")
        for colnum, column in enumerate(self.keyboard.columns.blocks):
            netname = coltpl.render(colnum = colnum)
            colnets = colnets + "  (net " + str(netnum) + " " + netname + ")\n"
            addnets = addnets + "    (add_net " + netname + ")\n"
            for keyindex in column:
                self.keyboard.keys[keyindex].colnetnum = netnum
            netnum += 1

        # ... and for each diode
        diodenets = ""
        diodetpl = self.jinja_env.get_template("layout/diodenetname.tpl")
        for diodenum in range(len(self.keyboard.keys)):
            netname = diodetpl.render(diodenum = diodenum)
            diodenets = diodenets + "  (net " + str(netnum) + " " + netname + ")\n"
            addnets = addnets + "    (add_net " + netname + ")\n"
            self.keyboard.keys[diodenum].diodenetnum = netnum
            netnum += 1

        nets = self.jinja_env.get_template('layout/nets.tpl')

        return nets.render(rownets = rownets, colnets = colnets, diodenets = diodenets, addnets = addnets), netnum        
        
    def generate_layout(self, args):
        """ Generate layout """
        
        print("Generating PCB layout ...")

        nets, numnets = self.define_nets()

        components, numcomponents = self.place_layout_components()

        layout = self.jinja_env.get_template('layout/layout.tpl')
        layoutOutputFilePath = args.outname + '/' + args.outname + '.kicad_pcb'
        with open(layoutOutputFilePath, 'w', newline='\n') as out_file:
            out_file.write(layout.render(modules=components, nummodules=numcomponents, nets=nets, numnets=numnets, vias="", traces="", numtracks = 0))

    def generate_project(self, args):
        prj = self.jinja_env.get_template('kicadproject.tpl')
        with open(args.outname + '/' + args.outname + '.pro', 'w', newline='\n') as out_file:
            out_file.write(prj.render())


# Program entry
if __name__ == '__main__':
    kbpcbgen = KLEPCBGenerator()
    kbpcbgen.generate_kicadproject()
    kbpcbgen.keyboard.printKeyInfo()
