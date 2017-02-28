import sys
import pickle
from fb_HTML_parser import FB_HTMLParser
import draw
from datetime import datetime, timedelta
from helper_fun import *
import my_excepthook

# The parsed data is saved, only if this is set to True the data will be parsed,
# otherwise the parser will be loaded from a previously created file
NEW_PARSER = False

# Number of days to sum up for one circle
DAYS_PER_CIRCLE = 14

# Minutes to sum up to one segment of a circle
DELTA_MINUTES = 15

def load_parser(new_parser, user_name):
    if(new_parser):
        print("Parse messenger data for user", user_name)
        parser = FB_HTMLParser(DELTA_MINUTES, user_name)
        # Feed data
        parser.feed(data)

        # Save parser
        f = open('store.pckl', 'wb')
        pickle.dump(parser, f)
        f.close()
    else:
        # Load custom parser from file
        print("Load message information from recent parsing")
        f = open('store.pckl', 'rb')
        parser = pickle.load(f)
        f.close()

    return parser

if __name__ == "__main__":
    user_name = sys.argv[1]

    # Get messenger information from html document
    with open('messages.htm', 'r') as myfile:
    #  with open('messages_fake_account.htm', 'r') as myfile:
        data = myfile.read()

    # Create custom html parser
    parser = load_parser(NEW_PARSER, user_name)

    # Process found data
    print("Process found data")

    data = parser.final_data

    current_date = list(data.keys())[0]
    final_date = list(data.keys())[-1]

    time_delta = timedelta(days=DAYS_PER_CIRCLE)
    next_date = current_date + time_delta

    data_draw = {}
    size_day = int(24*(60/DELTA_MINUTES))
    data_draw[current_date] = dict.fromkeys([x*DELTA_MINUTES for x in range(0,size_day)], 0)

    min_delta = timedelta(minutes=DELTA_MINUTES)
    current_day = current_date  # Start with the earliest date
    while next_date <= final_date:
        current_minutes = day_to_minutes(current_day)
        data_draw[current_date][current_minutes] += data[current_day]
        current_day += min_delta
        if current_day >= next_date:
            current_date = next_date
            next_date += time_delta
            data_draw[current_date] = dict.fromkeys([x*DELTA_MINUTES for x in range(0, size_day)], 0)

    # Remove last added date
    data_draw.pop(current_date, None)
    # Sort dictionary and minutes-dictionaries
    data_draw = OrderedDict(sorted(data_draw.items(), key=lambda t: t[0]))
    for key, item in data_draw.items():
        data_draw[key] = OrderedDict(sorted(item.items(), key=lambda t: t[0]))

    #  print("{" + "\n".join("{}: {}".format(k, v) for k, v in data_draw.items()) + "}")

    draw.draw_dates_circle(data_draw, thickness=DAYS_PER_CIRCLE, col_pow=0.2)

    ####### Sum up weekdays
    #  data_days = {'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0, 'Friday': 0, 'Saturday': 0, 'Sunday': 0}
    #  for key, item in parser.final_data.items():
        #  dayname = key.strftime("%A")
        #  data_days[dayname] += item

    #  draw.draw_weekdays(data_days)
    #######



    #  ordered_dict = OrderedDict(sorted(parser.message_user.items(), key = lambda t:t[1][0]))
    #  print("{" + "\n".join("{}: {}".format(k, v) for k, v in ordered_dict.items()) + "}")

