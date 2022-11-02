import argparse

from  klepcbgenmod import KLEPCBGenerator

PROGRAM_VERSION = "2.0"

def parse_command_line_arguments():
    """ Parse the command line and check that the correct number of arguments is given """
    parser = argparse.ArgumentParser(
        prog="klepcbgen",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Utility to generate a KiCad schematic and layout of the switch matrix of \
a keyboard designed using the Keyboard Layout Editor \
(http://www.keyboard-layout-editor.com/)",
    )
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + PROGRAM_VERSION
    )
    parser.add_argument(
        "-V", "--verbose", dest="verbose", action="store_true",
        help="Log details about what is going on"
    )

    parser.add_argument(
        "-c", dest="colgroup", choices=['seq', 'pos'], default='seq',
        help="Select the algorithm for grouping keys into columns"
    )

    parser.add_argument(
        "-o", dest="outname", required=True,
        help='The directory and base name for the output files (e.g. "id80" will result in "id80.sch" and \
                "id80.pcb" located in the "id80" subdirectory',
    )

    parser.add_argument(
        "-n", dest="routing", action="store_false",
        help='Do not add traces to (partly) connect switch rows and columns'
    )

    parser.add_argument(
        "infile",
        help="A JSON file containing a keyboard layout in the KLE JSON format",
    )

    args = parser.parse_args()

    return args

# Program entry
if __name__ == "__main__":
    arguments = parse_command_line_arguments()
    kbpcbgen = KLEPCBGenerator()
    kbpcbgen.generate_kicadproject(arguments.infile, arguments.outname, arguments.routing, arguments.colgroup)
    kbpcbgen.keyboard.print_key_info()