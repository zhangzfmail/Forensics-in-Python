##############################################################
#          Obtain User Input from System Argument            #
##############################################################
import argparse

def argParser():
    #Define initial information for argument parser
    description = 'Computer Forensic Tools'
    epilogue = 'Developed in Python'
    parser = argparse.ArgumentParser(description=description, epilog=epilogue)

    #Add arguments
    parser.add_argument('Position', help='Positional Arguments to Apply')
    parser.add_argument('--one', help='Optional Argument One')

    #Optional argument forced to be required
    parser.add_argument('--two', help='Optional Argument Two', required=True)

    #Optional argument using -t or --three
    parser.add_argument('-t', '--three', help='Optional Argument Three')

    #Assign False or True to value if present
    parser.add_argument('--four', help='Optional Argument Four', action="store_false")
    parser.add_argument('--five', help='Optional Argument Five', action="store_true")

    #Append values if present --six value
    parser.add_argument('--six', help='Optional Argument Six', action="append")

    #Count the number of instances -sss
    parser.add_argument('-s', help='Optional Argument Seven', action='count')

    #Add value by default
    parser.add_argument('--eight', default=55, type=int)
    parser.add_argument('--nine', default='GATech', type=str)

    #Open specified file for reading or writing
    parser.add_argument('input_file', type=argparse.FileType('r'))
    parser.add_argument('output_file', type=argparse.FileType('w'))

    #Allow only specified choices
    parser.add_argument('--ten', choices=['A', 'B', 'C'])

    #Parsing arguments into objects
    arguments = parser.parse_args()

    print arguments

argParser()
