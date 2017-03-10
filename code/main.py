import sys
import os
import pickle
from fb_HTML_parser import FB_HTMLParser
import draw
from datetime import datetime, timedelta
from helper_fun import *
from collections import OrderedDict
import my_excepthook

# The parsed data is saved, only if this is set to True the data will be parsed,
# otherwise the parser will be loaded from a previously created file
NEW_PARSER = False

# Number of days to sum up for one circle
DAYS_PER_CIRCLE = 7

# Minutes to sum up to one segment of a circle
DELTA_MINUTES = 5

# Blur of the data, to achieve better visualization
BLUR = 1.1

# Brightness - the higher the number, less data will be highlighted
BRIGHTNESS = 2.0

def load_parser(new_parser, user_name):
    if(new_parser):
        print("Parse messenger data for user", user_name)
        parser = FB_HTMLParser(DELTA_MINUTES, user_name)
        # Feed data, get messenger information from html document
        with open('../messages.htm', 'r') as myfile:
            data = myfile.read()
            parser.feed(data)

        # Save parser
        with open('store.pckl', 'wb') as f:
            pickle.dump(parser, f)
    else:
        # Load custom parser from file
        print("Load message information from recent parsing")
        with open('store.pckl', 'rb') as f:
            parser = pickle.load(f)

    return parser


if __name__ == "__main__":
    user_name = sys.argv[1]

    # Create custom html parser
    parser = load_parser(NEW_PARSER, user_name)

    # Process found data
    print("Process found data")

    data = parser.final_data

    # Blur the data for aussagekrätigere visualization
    data = gaus_blur(data, BLUR)

    #### Sort data
    #  data_draw = sort_data_days(data, DAYS_PER_CIRCLE, DELTA_MINUTES)

    #  print("{" + "\n".join("{}: {}".format(k, v) for k, v in data_draw.items()) + "}")

    #  draw.draw_dates_circle(data_draw, thickness=DAYS_PER_CIRCLE, col_pow=BRIGHTNESS)


    ###### Sum up each minute step
    size_day = int(24*(60/DELTA_MINUTES))
    data_minutes = OrderedDict.fromkeys([x*DELTA_MINUTES for x in range(0,size_day)], 0)

    current_date = list(data.keys())[0]
    final_date = list(data.keys())[-1]
    final_date = final_date.replace(hour=0, minute=0)

    min_delta = timedelta(minutes=DELTA_MINUTES)
    current_minutes = 0

    while current_date < final_date:
        data_minutes[current_minutes] += data[current_date]

        # Increment by one minute step
        current_date += min_delta
        current_minutes = (current_minutes + DELTA_MINUTES)%(24*60)

    draw.draw_minutes_circle(data_minutes)


    ####### Sum up weekdays
    #  data_days = {'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0, 'Friday': 0, 'Saturday': 0, 'Sunday': 0}
    #  for key, item in parser.final_data.items():
        #  dayname = key.strftime("%A")
        #  data_days[dayname] += item

    #  print(data_days)


    #  draw.draw_weekdays(data_days)
    #######
