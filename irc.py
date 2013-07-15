# irc.py: Classes relating to the IRC protocol

import socket
import threading, queue
import logging

TIMEOUT = 1800

class IRCServer:
    encoding = "utf-8" # fallback ISO-8859-1?
    term = "\r\n"
    nick = None

    def __init__(self, handler, addr, port=6667, ssl=False):
        self.network = addr
        self.port = port
        self.ssl = ssl # TODO
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.queue = queue.Queue()
        self.isconnected = False
        self.handler = handler

    def connect(self):
        self.sock.connect((self.network, self.port))
        self.isconnected = True

    def raw(self, line):
        self.sock.send((line+self.term).encode(self.encoding))

    def send(self, cmd, params):
        cmd = cmd.upper()
        self.raw(cmd+" "+params)

    def recv(self):
        data = self.sock.recv(4096).decode(self.encoding)
        return data
    
    def handshake(self, user="sadaharu", name="Sadaharu", nick="sadaharu", pswd=None, host="-", server="-"):
        self.nick = nick
        self.sock.settimeout(16)
        self.connect()
        try:
            print(self.recv())
        except socket.timeout:
            pass
        self.sock.settimeout(TIMEOUT)
        self.send("NICK", nick)
        self.send("USER", "%s %s %s %s" %(user, host, server, name))
        if pswd:
            self.send("PASS", pswd)

s = IRCServer(None, "irc.awfulnet.org", 6667)
s.handshake()
def run(s):
    while s.isconnected:
        print(s.recv())
threading.Thread(target=run, args=(s,)).start()
while s.isconnected:
    s.raw(input('> '))
