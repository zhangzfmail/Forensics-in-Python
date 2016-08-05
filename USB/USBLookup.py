##############################################################
#          Obtain User Input from System Argument            #
##############################################################
import urllib2
import sys

def getRecord(record_line):
    split = record_line.find(' ')
    record_id = record_line[:split]
    record_name = record_line[split + 1:]
    return record_id, record_name

def search_key(usb_dict):
    try:
        vendor_key = sys.argv[1]
        product_key = sys.argv[2]
    except IndexError:
        print 'USBLookup <Vendor ID> and <Product ID>'
        sys.exit(1)

    try:
        vendor = usb_dict[vendor_key][0]
    except KeyError:
        print 'Vendor ID not found.'
        sys.exit(0)
    try:
        product = usb_dict[vendor_key][1][product_key]
    except KeyError:
        print 'Product ID not found from Vendor: %s' % vendor
        sys.exit(0)
    print 'Product: %s from Vendor: %s ' % (product, vendor)

def webLookup():
    url = 'http://www.linux-usb.org/usb.ids'
    usbs = {}
    usb_file = urllib2.urlopen(url)
    current_id = ''

    for line in usb_file:
        #Ignore the comment and newline
        if line.startswith('#') or line == '\n':
            pass
        else:
            #Obtain major USB ID and Name
            if not(line.startswith('\t')) and (line[0].isdigit() or line[0].islower()):
                usb_id, name = getRecord(line.strip())
                current_id = usb_id
                usbs[usb_id] = [name, {}]
            #Obtain minor USB ID and Name
            elif line.startswith('\t') and line.count('\t') == 1:
                usb_id, name = getRecord(line.strip())
                usbs[current_id][1][usb_id] = name

    search_key(usbs)

def localLookup():
    usb_file = open("usb.dat", "r")
    usbs = {}
    current_id = ''

    for line in usb_file:
        #Ignore the comment and newline
        if line.startswith('#') or line == '\n':
            pass
        else:
            #Obtain major USB ID and Name
            if not(line.startswith('\t')) and (line[0].isdigit() or line[0].islower()):
                usb_id, name = getRecord(line.strip())
                current_id = usb_id
                usbs[usb_id] = [name, {}]
            #Obtain minor USB ID and Name
            elif line.startswith('\t') and line.count('\t') == 1:
                usb_id, name = getRecord(line.strip())
                usbs[current_id][1][usb_id] = name

    search_key(usbs)
