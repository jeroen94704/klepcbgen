import sys
from  klepcbgenmod import *
import argparse

def parse_command_line_arguments():
    """ Parse the command line and check that the correct number of arguments is given """
    parser = argparse.ArgumentParser(
        prog="klepcbgen",
        description="Utility to generate a KiCad schematic and layout of the switch matrix of \
a keyboard designed using the Keyboard Layout Editor \
(http://www.keyboard-layout-editor.com/)",
    )
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + PROGRAM_VERSION
    )
    parser.add_argument(
        "infile",
        help="A JSON file containing a keyboard layout in the KLE JSON format",
    )
    parser.add_argument(
        "outname",
        help='The base name of the output files (e.g. "id80" will result in "id80.sch" and \
                "id80.pcb"',
    )
    parser.add_argument(
        "--no-grid-background-tracks", action="store_true",
        help="Don't add background-layer tracks to each button.",
        default=False
    )
    parser.add_argument(
        "--no-grid-foreground-tracks", action="store_true",
        help="Don't add foreground-layer tracks to each button.",
        default=False
    )

    args = parser.parse_args()

    if not args.infile:
        print("")
        parser.error(
            "Not all required arguments are present. Use the options '-h' for more information"
        )

    return args

# Program entry
if __name__ == "__main__":
    arguments = parse_command_line_arguments()
    kbpcbgen = KLEPCBGenerator()
    kbpcbgen.generate_kicadproject(arguments)
    kbpcbgen.keyboard.print_key_info()
