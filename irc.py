# irc.py: Classes relating to the IRC protocol

import sys
import ssl
import time
import select
import socket

from event import AbstractEvent

TIMEOUT = 1800

class IRCServer:
    def __init__(self, bot, addr, port=6667, _ssl=False):
        self.bot = bot
        self.network = addr
        self.port = port
        self.ssl = _ssl
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.ssl:
            self.sock = ssl.wrap_socket(self.sock)
        self.isconnected = False
        self.encoding = "utf-8" # fallback ISO-8859-1?
        self.term = "\r\n"
        self.nick = bot.conf.get("nick", "sadaharu")
        self.pswd = bot.conf.get("pass", None)

    def connect(self):
        self.sock.connect((self.network, self.port))
        self.isconnected = True

    def disconnect(self):
        self.isconnected = False
        self.sock.close()

    def raw(self, line):
        class RSendEvent(AbstractEvent):
            name = "SENDRAW"
            def __init__(self, line):
                AbstractEvent.__init__(self)
                self.line = line
        line = RSendEvent(line).fire(self.bot).line
        try:
            self.sock.send((line+self.term).encode(self.encoding))
        except:
            errtype, value, tb = sys.exc_info()
            print("[Socket closed] %s: %s"%(errtype.__name__, value))
            self.disconnect()

    def recv(self):
        class RReadEvent(AbstractEvent):
            name = "READRAW"
            def __init__(self, line):
                AbstractEvent.__init__(self)
                self.line = line
        data = self.sock.recv(4096).decode(self.encoding, "replace")
        while data[-2:] != self.term:
            data += self.sock.recv(1024).decode(self.encoding, "replace")
        return [RReadEvent(l).fire(self.bot).line for l in data.split(self.term)]
    
    def handshake(self, user="sadaharu", name="Sadaharu", host="*", server="*"):
        self.sock.settimeout(16)
        self.connect()
        self.sock.settimeout(TIMEOUT)
        self.raw("NICK "+self.nick)
        self.raw("USER %s %s %s %s" %(user, host, server, name))
        if self.pswd:
            self.raw("PASS "+self.pswd)
        for line in self.recv():
            self.bot.handler.handle(line)

    def identify(self, passwd, service="NickServ"):
        self.raw("PRIVMSG %s identify %s" %(service, passwd))

    def ready(self):
        return select.select([self.sock], [], [], 1)[0]
