# user.py: Classes relating to users

from static import *

class User:
    def __init__(self, bot, nick):
        self.nick = nick
        self.modes = set()
        self.chans = {}
        self.prefix = ' '

    def add(self, chan):
        self.chans.add(chan)

    def genprefix(self, chan):
        for m in umodes:
            if m in self.chans[chan]:
                self.prefix = umodes[m]
                return self.prefix
        self.prefix = ' '
        return self.prefix
