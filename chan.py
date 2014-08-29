# chan.py: Classes relating to channels

import os
from collections import deque

class Channel:
    def __init__(self, bot, name):
        self.name = name
        self.modes = set()
        self.log = {"*all": deque([], 16386)}

    def users(self):
        return [x for n,x in self.bot.users.items() if self.name in x.chans.keys()]

    def getlog(self, name):
        try:
            return self.log[name]
        except KeyError:
            self.log[name] = deque([], 64)
            return self.log[name]
