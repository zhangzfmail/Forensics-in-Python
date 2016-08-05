##############################################################
#          Obtain User Input from System Argument            #
##############################################################
import sys 


def userInput():
    args = sys.argv
    print 'Pythonn Script Executed: ', args[0]
    args.pop(0)
    for i, argument in enumerate(sys.argv):
        print 'Argument Number %d: %s' % (i, argument)
        print 'Argument Type: %s' % type(argument)
