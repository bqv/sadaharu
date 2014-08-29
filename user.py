# user.py: Classes relating to users

from static import *

class User:
    def __init__(self, hostmask):
        self.nick = None
        self.host = None
        self.user = None

        if hostmask:
            self.hostmask = hostmask
            if '@' in self.hostmask:
                l = self.hostmask.split('@')
                self.host = l[1]
                if '!' in l[0]:
                    l = l[0].split('!')
                    self.nick = l[0]
                    self.user = l[1]
                else:
                    self.nick = l[0]
            else:
                nick = hostmask
        else:
            nick = "!"

        self.name = None
        self.hops = None
        self.server = None
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

    def __repr__(self):
        return self.nick
