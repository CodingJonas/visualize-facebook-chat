import re
import dateutil.parser
from datetime import timedelta, datetime
import pytz
from collections import OrderedDict

def day_to_minutes(sourcedate):
    minutes = sourcedate.minute
    minutes += sourcedate.hour * 60
    return minutes

def add_months(sourcedate,months):
    _month = sourcedate.month + months
    _year = sourcedate.year + int(_month/13)
    _month = _month % 13 + int(_month/13)
    return sourcedate.replace(year=_year, month=_month)

def hasNumbers(inputString):
    return bool(re.search(r'\d', inputString))

def replaceDE_EN(data):
    data = data[re.search(",", data).start():]
    data = data.replace("Januar ", "Jan ")
    data = data.replace("Februar ", "Feb ")
    data = data.replace("März ", "Mar ")
    data = data.replace("April ", "Apr ")
    data = data.replace("Mai ", "May ")
    data = data.replace("Juni ", "Jun ")
    data = data.replace("Juli ", "Jul ")
    data = data.replace("August ", "Aug ")
    data = data.replace("September ", "Sep ")
    data = data.replace("Oktober ", "Oct ")
    data = data.replace("November ", "Nov ")
    data = data.replace("Dezember ", "Dec ")
    data = data.replace("um", "at")
    return data

def getDate(data, minutes_delta):
    # Replace German expressions with English ones
    date = replaceDE_EN(data)
    date = dateutil.parser.parse(date)
    # Set number of minutes to a certain number
    minutes = date.minute
    minutes -= minutes%minutes_delta
    date = date.replace(minute=minutes)
    # tzinfo is not important as always the local time matters
    date = date.replace(tzinfo=None)
    return date

def init_final_data(minutes_delta):
    date_dict = {}
    cur_date = datetime(2010, 10, 6, 0)
    max_date = datetime.now().replace(minute=0, second=0, microsecond=0)
    delta_time = timedelta(minutes=minutes_delta)
    while cur_date <= max_date:
        date_dict[cur_date] = 0
        cur_date += delta_time
    date_dict = OrderedDict(sorted(date_dict.items(), key=lambda t: t[0]))
    return date_dict

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print()
