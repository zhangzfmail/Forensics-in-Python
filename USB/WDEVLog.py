##############################################################
#               Parse Windows Device Log File                #
#             Windows XP: C:\Windows\setupapi.log            #
#          Windows 7: C:\Windows\inf\setupapi.dev.log        #
##############################################################
import argparse
import os
import sys
import USBLookup

def main():
    parser = argparse.ArgumentParser(description='Windows Device Log',
                                     epilog='Developed in Python')
    parser.add_argument('Device_Log', help='Windows 7 SetupAPI File')
    args = parser.parse_args()

    in_file = args.Device_Log

    if os.path.isfile(in_file):
        device_information = parseSetupapi(in_file)
        usb_ids = prepUSBLookup()
        for device in device_information:
            parsed_info = parseDeviceInfo(device)
            if isinstance(parsed_info, dict):
                parsed_info = getDeviceNames(usb_ids, parsed_info)
            if parsed_info is not None:
                printOutput(parsed_info)
        print 'Windows device log parsed and printed successfully'

    else:
        print 'Windows device log not found'
        sys.exit(1)


def parseSetupapi(setup_log):
    device_list = list()
    unique_list = set()
    log_file = open(setup_log, "r")
    for line in log_file:
        lower_line = line.lower()
        if 'device install (hardware initiated)' in lower_line and ('vid' in lower_line or 'ven' in lower_line):
            device_name = line.split('-')[1].strip()
            date = next(log_file).split('start')[1].strip()
            if device_name not in unique_list:
                device_list.append((device_name, date))
                unique_list.add(device_name)

    return device_list


def parseDeviceInfo(device_info):
    # Initialize variables
    vid = ''
    pid = ''
    rev = ''
    uid = ''

    # Split string into segments on \\
    segments = device_info[0].split('\\')

    if 'usb' not in segments[0].lower():
        #Eliminate non-USB devices from output which may hide othe rstorage devices
        return None

    for item in segments[1].split('&'):
        lower_item = item.lower()
        if 'ven' in lower_item or 'vid' in lower_item:
            vid = item.split('_',1)[-1]
        elif 'dev' in lower_item or 'pid' in lower_item or 'prod' in lower_item:
            pid = item.split('_',1)[-1]
        elif 'rev' in lower_item or 'mi' in lower_item:
            rev = item.split('_',1)[-1]

    if len(segments) >= 3:
        uid = segments[2].strip(']')

    if vid != '' or pid != '':
        return {'Vendor ID': vid.lower(), 'Product ID': pid.lower(),
                'Revision': rev, 'UID': uid,
                'First Installation Date': device_info[1]}
    else:
        # Unable to parse data, returning whole string
        return device_info


def prepUSBLookup():
    try:
        #Obtain USB Vendor and Product Information
        usb_file = USBLookup.getUSBFile()
    except:
        #Obtain USB Vendor and Product Information Locally
        print "Plese Provide USB Vendor and Product Database"
        sys.exit(1)
    return USBLookup.parseFile(usb_file)


def getDeviceNames(usb_dict, device_info):
    device_name = USBLookup.searchKey(usb_dict, [device_info['Vendor ID'], device_info['Product ID']])

    device_info['Vendor Name'] = device_name[0]
    device_info['Product Name'] = device_name[1]

    return device_info


def printOutput(usb_information):
    print '-'*40

    if isinstance(usb_information, dict):
        for key_name, value_name in usb_information.items():
            print '%s: %s' % (key_name, value_name)
    elif isinstance(usb_information, tuple):
        print 'Device: %s' % (usb_information[0])
        print 'Date: %s' % (usb_information[1])

if __name__ == '__main__':
    main()
