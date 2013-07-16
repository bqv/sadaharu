# sadaharu.py: Main file - This project is subject to the terms of MPL v2.0; see LICENSE

import sys
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
        self.server = IRCServer(self, "irc.awfulnet.org", 6667)
        self.handler = Handler(self)
        self.event = Events(self)

    def start(self):
        print("Sadaharu!")
        self.run()

    def run(self):
        self.server.handshake()
        def loop(s):
            while s.isconnected:
                for line in s.recv():
                    self.handler.handle(line)
        threading.Thread(target=loop, args=(self.server,)).start()
        while self.server.isconnected:
            self.server.raw(input('> '))

    def privmsg(self, targ, msg):
        self.server.send("PRIVMSG", "%s :%s" %(targ, msg))

if __name__ == "__main__":
    me = Sadaharu()
    me.start()
