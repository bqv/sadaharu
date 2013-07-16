# sadaharu.py: Main file - This project is subject to the terms of MPL v2.0; see LICENSE

import sys, os
import json
import logging, logging.handlers
import threading, queue

from irc import IRCServer
from event import Handler, Events

class Sadaharu:
    def __init__(self):
        self.log = logging.getLogger()
        self.log.setLevel(logging.INFO)
        self.log.addHandler(logging.handlers.RotatingFileHandler("sadaharu.log", 'a', 16*1024*1024, 99))
        self.log.addHandler(logging.StreamHandler(sys.stdout))
        self.conf = json.loads(open("conf.json").read())
        self.server = IRCServer(self, self.conf['server'], self.conf['port'])
        self.handler = Handler(self)
        self.event = Events(self)
        self.plugins = self.getplugins()

    def start(self):
        print("Sadaharu!")
        self.run()

    def run(self):
        self.server.handshake()
        self.server.identify(self.conf['nickpass'])
        def loop(s):
            while s.isconnected:
                for line in s.recv():
                    self.handler.handle(line)
        threading.Thread(target=loop, args=(self.server,)).start()
        while self.server.isconnected:
            self.server.raw(input('> '))

    def privmsg(self, targ, msg):
        self.server.send("PRIVMSG", "%s :%s" %(targ, msg))

    def getplugins(self):
        self.cdir = os.path.dirname(os.path.realpath(__file__))
        self.pdir = os.path.join(self.cdir, "plugins")
        sys.path.insert(0, self.cdir)
        sys.path.insert(0, self.pdir)
        plugins = set([__import__(p[:-3]) for p in os.listdir(self.pdir) if p.endswith(".py")])
        plugincount = len(plugins)

if __name__ == "__main__":
    me = Sadaharu()
    me.start()
