# chan.py: Classes relating to channels

import os
from collections import deque

class Channel:
    def __init__(self, bot, name):
        self.name = name
        self.modes = set()
        self._logs = bot.data['logs'] = bot.data.get('logs', dict())
        self._logs[self.name] = dict({None: deque([], 16386)})

    def users(self):
        return [x for n,x in self.bot.users.items() if self.name in x.chans.keys()]

    def getlog(self, name=None):
        try:
            return self._logs[self.name][name]
        except KeyError:
            self._logs[self.name][name] = deque([], 64)
            return self._logs[self.name][name]
