#!/usr/bin/python3
# sadaharu.py: Main file - This project is subject to the terms of MPL v2.0; see LICENSE

import sys, os
import json
import logging, logging.handlers
import threading, queue

from irc import IRCServer
from handler import Handler
from hooks import Hook
from event import Events

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
        self.chans = dict()
        self.users = dict()
        Hook.bot = self
        self.plugins = self.loadplugins()

    def start(self):
        print("Sadaharu!")
        self.run()

    def run(self):
        self.server.handshake()
        while self.server.isconnected:
            for line in self.server.recv():
                self.handler.handle(line)

    def privmsg(self, targ, msg):
        self.send("PRIVMSG", "%s :%s" %(targ, msg))

    def loadplugins(self):
        self.cdir = os.path.dirname(os.path.realpath(__file__))
        self.pdir = os.path.join(self.cdir, "plugins")
        sys.path.insert(0, self.cdir)
        sys.path.insert(0, self.pdir)
        plugins = set([__import__(p[:-3]) for p in os.listdir(self.pdir) if p.endswith(".py")])
        plugincount = len(plugins)

    def getnick(self):
        return self.server.nick

    def send(self, cmd, params=None):
        (cmd, params) = self.event.call("SEND", (cmd, params))
        self.log.debug("-> "+cmd+(" "+params if params else ""))
        cmd = cmd.upper()
        if params:
            self.server.raw(cmd+" "+params)
        else:
            self.server.raw(cmd)

if __name__ == "__main__":
    me = Sadaharu()
    me.start()
