##############################################################
#                  ROT-13 Encode and Decode                  #
##############################################################
import argparse
import os

def main():
    #Define system argument
    parser = argparse.ArgumentParser(description='ROT-13 Encode and Decode',
                                     epilog='Developed in Python')
    parser.add_argument('FILE', help='Name of file for encoding or decoding')
    parser.add_argument('-T', help='Output file path')
    args = parser.parse_args()

    infile = args.FILE

    #Assign outputfile location
    if args.T:
        if not os.path.exists(args.T):
            os.makedirs(args.T)
        outfile = os.path.join(args.T, 'output_file.txt')
    else:
        outfile = 'output_file.txt'

    #Encode or decode file
    input_file = open(infile, "r")
    output_file = open(outfile, "a")
    for line in input_file:
        result = rotCode(line)
        output_file.write(result)

def rotCode(data):
    rot_chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    substitutions = []
    #Walk through each individual character
    for c in data:
        if c.isupper():
            try:
                #Find the position of the character in rot_chars list
                index = rot_chars.index(c.lower())
            except ValueError:
                substitutions.append(c)
                continue
            #Calculate the relative index that is 13 characters away from the index
            substitutions.append((rot_chars[(index-13)]).upper())
        else:
            try:
                #Find the position of the character in rot_chars list
                index = rot_chars.index(c)
            except ValueError:
                substitutions.append(c)
                continue
            substitutions.append(rot_chars[((index-13))])

    return ''.join(substitutions)
    
if __name__ == '__main__':
     main()
