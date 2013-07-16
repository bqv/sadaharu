# irc.py: Classes relating to the IRC protocol

import time
import socket

TIMEOUT = 1800

class IRCServer:
    def __init__(self, bot, addr, port=6667, ssl=False):
        self.bot = bot
        self.network = addr
        self.port = port
        self.ssl = ssl # TODO
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.isconnected = False
        self.encoding = "utf-8" # fallback ISO-8859-1?
        self.term = "\r\n"
        self.nick = None

    def connect(self):
        self.sock.connect((self.network, self.port))
        self.isconnected = True

    def disconnect(self):
        self.isconnected = False
        self.sock.close()

    def raw(self, line):
        (line,) = self.bot.event.call("SENDRAW", (line,))
        self.sock.send((line+self.term).encode(self.encoding))

    def send(self, cmd, params=None):
        (cmd, params) = self.bot.event.call("SEND", (cmd, params))
        cmd = cmd.upper()
        if params:
            self.raw(cmd+" "+params)
        else:
            self.raw(cmd)

    def recv(self):
        data = self.sock.recv(4096).decode(self.encoding)
        return [self.bot.event.call("READRAW", (l,))[0] for l in data.split(self.term)]
    
    def handshake(self, user="sadaharu", name="Sadaharu", nick="sadaharu", pswd=None, host="-", server="-"):
        self.nick = nick
        self.sock.settimeout(16)
        self.connect()
        try:
            for line in self.recv():
                self.bot.handler.handle(line)
        except socket.timeout:
            pass
        self.sock.settimeout(TIMEOUT)
        self.send("NICK", nick)
        self.send("USER", "%s %s %s %s" %(user, host, server, name))
        if pswd:
            self.send("PASS", pswd)
        time.sleep(2)
        for line in self.recv():
            self.bot.handler.handle(line)
        self.send("MODE", nick+" +B")

    def identify(self, passwd, service="NickServ"):
        self.send("PRIVMSG", "%s identify %s" %(service, passwd))

