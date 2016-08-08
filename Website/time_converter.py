##############################################################
#               Convert Timestamps into a UTC                #
##############################################################
import datetime

def main():
    time_stamp = int(raw_input('Unix Timestamp: >> '))
    print time_converter(time_stamp)

def time_converter(timestamp):
    date_time = datetime.datetime.utcfromtimestamp(timestamp)
    return date_time.strftime('%m/%d/%Y %I:%M:%S %p')

if __name__ == '__main__':
    main()
