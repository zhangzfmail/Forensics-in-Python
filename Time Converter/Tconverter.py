##############################################################
#               Convert Timestamps into a UTC                #
##############################################################
import datetime

def time_converter(timestamp):
    #Change the timestamp into integer type
    time = int(timestamp)
    date_time = datetime.datetime.utcfromtimestamp(time)
    return date_time.strftime('%m/%d/%Y %I:%M:%S %p UTC')
