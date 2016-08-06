import urllib2
import sys

def main():
    if len(sys.argv) >= 3:
        ids = (sys.argv[1],sys.argv[2])
    else:
        print "Please Provide the Vendor and Product ID"
        sys.exit(1)

    usb_file = getUSBFile()
    usbs = parseFile(usb_file)
    results = searchKey(usbs, ids)
    print "Vendor: %s" % (results[0])
    print "Product: %s" % (results[1])

def getUSBFile():
    try:
        #Obtain USB Vendor and Product Information Online
        url = 'http://www.linux-usb.org/usb.idsabc'
        usb_file = urllib2.urlopen(url)
    except:
        #Obtain USB Vendor and Product Information Locally
        usb_file = open("usb.dat", "r")
    return usb_file


def parseFile(usb_file):
    usbs = {}
    curr_id = ''
    for line in usb_file:
        if line.startswith('#') or line == '\n':
            pass
        else:
            if not line.startswith('\t') and (line[0].isdigit() or line[0].islower()):
                id, name = getRecord(line.strip())
                curr_id = id
                usbs[id] = [name, {}]
            elif line.startswith('\t') and line.count('\t') == 1:
                id, name = getRecord(line.strip())
                usbs[curr_id][1][id] = name
    return usbs


def getRecord(record_line):
    split = record_line.find(' ')
    record_id = record_line[:split]
    record_name = record_line[split + 1:]
    return record_id, record_name


def searchKey(usb_dict, ids):
    vendor_key = ids[0]
    product_key = ids[1]
    try:
        vendor = usb_dict[vendor_key][0]
    except KeyError:
        vendor = 'Unknown'
    try:
        product = usb_dict[vendor_key][1][product_key]
    except KeyError:
        product = 'Unknown'
    return vendor, product


if __name__ == '__main__':
    main()
