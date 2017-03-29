from html.parser import HTMLParser
from collections import OrderedDict
from helper_fun import *


class FB_HTMLParser(HTMLParser):
    def __init__(self, delta_minutes, user_name):
        HTMLParser.__init__(self)

        self.delta_minutes = delta_minutes
        self.user_name = user_name

        self.nextData = 'nothing'  # important to map next message to a user
        self.div_level = 0
        self.div_level_message = -1
        self.last_date = 0
        self.last_user = 'None'

        self.final_data = init_final_data(self.delta_minutes)
        self.message_user = {}

    def handle_starttag(self, tag, attrs):
        if tag != 'div' and tag !='span':
            return
        if tag == 'div':
            self.div_level += 1
        for attr in attrs:
            self.nextData = attr[1]
            if attr[1] == 'message':
                self.div_level_message = self.div_level

    def handle_endtag(self, tag):
        if tag == 'div':
            self.div_level -= 1
            if self.div_level == self.div_level_message-1:
                self.nextData = 'message'


    def handle_data(self, data):
        if self.nextData == 'meta':
            self.handle_meta(data)
        elif self.nextData == 'user':
            self.handle_user(data)
        elif self.nextData == "message":
            self.handle_message(data)
        self.nextData = 'nothing'

    def handle_meta(self, data):
        date = getDate(data, self.delta_minutes)
        self.last_date = date

    def handle_user(self, data):
        # Some names are not saved properly
        # you can often figure out from messages who it is and simply replace it
        if data == '100000489284947@facebook.com':
            data = "Max Power"
        self.last_user = data

    def handle_message(self, data):
        # Only save messages I wrote
        if self.last_user == self.user_name:
            self.final_data[self.last_date] += len(data)
        # Add number of messages per user
        if self.last_user in self.message_user.keys():
            self.message_user[self.last_user][0] += len(data)
            self.message_user[self.last_user][1] += 1
        else:
            self.message_user[self.last_user] = [len(data), 1]
