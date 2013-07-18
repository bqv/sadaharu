# chan.py: Classes relating to channels

class Channel:
    def __init__(self, bot, name):
        self.name = name
        self.modes = set()
