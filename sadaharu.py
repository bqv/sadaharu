#!/usr/bin/python3
# sadaharu.py: Main file - This project is subject to the terms of MPL v2.0; see LICENSE

import sys, os
import json
import queue
import select
import logging, logging.handlers
import threading, queue

from irc import IRCServer
from handler import Handler
from hooks import Hook
from event import Events

class Bot(threading.Thread):
    def __init__(self, ring, name, conf):
        threading.Thread.__init__(self)
        self.ring = ring
        self.name = name
        self.conf = conf
        self.data = dict()
        self.log = logging.getLogger(self.name)
        self.log.setLevel(logging.INFO)
        self.log.addHandler(logging.handlers.RotatingFileHandler(self.name+".log", 'a', 16*1024*1024, 99))
        self.log.addHandler(logging.StreamHandler(sys.stdout))
        self.enabled = not self.conf.get('disabled', False)
        self.server = IRCServer(self, self.conf['server'], self.conf['port'], self.conf.get('ssl', False))
        self.handler = Handler(self)
        self.event = Events(self)
        self.sendqueue = queue.PriorityQueue()
        self.chans = dict()
        self.users = dict()
        self.plugins = self.loadplugins()

    def run(self):
        print("Sadaharu! - @"+self.name)
        self.server.handshake()
        while self.server.isconnected:
            try:
                line = self.sendqueue.get(False)
                self.server.raw(line)
                self.sendqueue.task_done()
            except queue.Empty:
                if self.server.ready():
                    for line in self.server.recv():
                        self.handler.handle(line)

    def privmsg(self, targ, msg):
        for line in str(msg).split('\n'):
            self.send("PRIVMSG", "%s :%s" %(targ, line))

    def notice(self, targ, msg):
        for line in str(msg).split('\n'):
            self.send("NOTICE", "%s :%s" %(targ, line))

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
        self.log.debug("[%s]-> "%(self.name,)+cmd+(" "+params if params else ""))
        cmd = cmd.upper()
        if params:
            self.sendqueue.put(cmd+" "+params)
        else:
            self.sendqueue.put(cmd)

class Sadaharu:
    def __init__(self):
        self.conf = json.loads(open("conf.json").read())
        self.bots = {}
        for kv in self.conf.items():
            self.addbot(*kv)
            
    def addbot(self, name, conf):
        self.bots[name] = Bot(self.bots, name, conf)

    def start(self):
        for bot in self.bots.values():
            if bot.enabled:
                bot.start()

if __name__ == "__main__":
    me = Sadaharu()
    me.start()
