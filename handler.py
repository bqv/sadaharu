# handler.py: Classes relating to raw message handling

import sys
import time
import re

from event import CancelEvent
from static import *
from chan import Channel
from user import User

class Handler:
    def __init__(self, bot):
        self.bot = bot
        self.cmdprefix = bot.conf['prefix']
        self.registered = {"PING": self.onping, "PRIVMSG": self.onprivmsg,
                "NOTICE": self.onnotice, "ERROR": self.onerror, "JOIN": self.onjoin,
                "NICK": self.onnickchange, "MODE": self.onmode}

    def handle(self, line):
        if not line:
            return

        self.bot.log.debug(line)

        if line[0] == ':':
            line = line.split(' ', 2)
            prefix = line[0][1:]
            line = line[1:]
        else:
            prefix = None
            line = line.split(' ', 1)

        command = line[0]
        try:
            params = line[1]
        except IndexError:
            params = None

        user = self.getuser(prefix)

        try:
            (command, user, params) = self.bot.event.call("READ", (command, user, params))

            if command in self.registered.keys():
                self.registered[command](user, params)
            elif len(command) == 3 and command.isdigit():
                self.onnumeric(command, user, params)
            else:
                self.bot.log.warning("Couldn't process unregistered command: %s %s", command, params)
        except CancelEvent:
            return

    def getuser(self, prefix):
        if prefix:
            if '@' in prefix:
                l = prefix.split('@')
                host = l[1]
                if '!' in l[0]:
                    l = l[0].split('!')
                    nick = l[0]
                    user = l[1]
                else:
                    nick = l[0]
                    user = ""
            else:
                nick = host = prefix
                user = ""
        else:
            host = nick = user = ""
        return {'host': host, 'nick': nick, 'user': user, 'full': prefix}

    def onping(self, prefix, params):
        (params,) = self.bot.event.call("PING", (params,))
        self.bot.server.send("PONG", params)

    def onprivmsg(self, user, msg):
        msg = msg.split(' ', 1)
        to = msg[0]
        msg = rawmsg = msg[1][1:]
        (targ,msg) = gettarget(user['nick'], msg)
        (user, to, targ, msg) = self.bot.event.call("PRIVMSG", (user, to, targ, msg))
        if iscommand(self.cmdprefix, msg):
            self.bot.event.call("COMMAND", (user, to, targ)+getcommand(self.cmdprefix, msg))
        t = time.localtime()
        timestamp = "[%02d:%02d:%02d] " %(t.tm_hour, t.tm_min, t.tm_sec)
        message = "[%s] <%s> %s" %(to, user['nick'], rawmsg)
        self.bot.log.info("%s%s" %(timestamp, message))

    def onnotice(self, user, msg):
        msg = msg.split(' ', 1)
        to = msg[0]
        msg = msg[1][1:]
        (user, to, msg) = self.bot.event.call("NOTICE", (user, to, msg))
        t = time.localtime()
        timestamp = "[%02d:%02d:%02d] " %(t.tm_hour, t.tm_min, t.tm_sec)
        notice = "[%s] -%s- %s" %(to, user['nick'], msg)
        self.bot.log.info("%s%s" %(timestamp, notice))

    def onnickchange(self, user, newnick):
        (newnick,) = self.bot.event.call("NICK", (newnick[1:],))
        if user['nick'] == self.bot.getnick():
            self.bot.server.nick = newnick
        else:
            self.bot.users[newnick] = self.bot.users.pop(user['nick'])

    def onjoin(self, user, chan):
        (user, chan) = self.bot.event.call("JOIN", (user, chan[1:]))
        nick = user['nick']
        if not chan in self.bot.chans.keys():
            self.bot.chans[chan] = Channel(self.bot, chan)
        if not nick in self.bot.users.keys():
            self.bot.users[nick] = User(self.bot, nick)
        self.bot.users[nick].chans[chan] = set()

    def onmode(self, user, params):
        p = params.split()
        def unpack(x):
            n = (re.sub("([+-])([A-Za-z]+)([A-Za-z])", "\g<1>\g<2>\g<1>\g<3>", x),x)
            return re.findall('..',n[0]) if n[0] == n[1] else unpack(n[0]);
        to = p[0]
        modes = unpack(p[1].lstrip(':'))
        users = p[2:]
        (user, to, modes, users) = self.bot.event.call("MODE", (user, to, modes, users))
        for m in modes:
            if m[1] in umodes:
                u = users.pop(0)
                if m[0] == '+':
                    self.bot.users[u].chans[to].add(m[1])
                else:
                    self.bot.users[u].chans[to].remove(m[1])
                self.bot.users[u].genprefix(to)
            elif to == self.bot.getnick():
                if m[0] == '+':
                    self.bot.users[to].modes.add(m[1])
                else:
                    self.bot.users[to].modes.remove(m[1])
            else:
                if m[0] == '+':
                    self.bot.chans[to].modes.add(m[1])
                else:
                    self.bot.chans[to].modes.remove(m[1])

    def onnumeric(self, response, user, msg):
        (response, user, msg) = self.bot.event.call("RESPONSE", (response, user, msg))
        if response == "001":
            self.onwelcome()
        elif response == "353":
            self.onnames(msg)
        t = time.localtime()
        timestamp = "[%02d:%02d:%02d] " %(t.tm_hour, t.tm_min, t.tm_sec)
        notice = "%s %s %s" %(response, user['full'], msg)
        self.bot.log.info("%s%s" %(timestamp, notice))

    def onwelcome(self):
        self.bot.event.call("WELCOME", ())
        self.bot.users[self.bot.getnick()] = User(self.bot, self.bot.getnick())
        self.bot.server.send("MODE", self.bot.getnick()+" +B")
        nickserv = self.bot.conf.get('nickserv', None)
        nickpass = self.bot.conf.get('nickpass', None)
        if nickpass:
            if nickserv:
                self.bot.server.identify(nickpass, nickserv)
            else:
                self.bot.server.identify(nickpass)

    def onnames(self, params):
        args = params.split(' ', 3)
        assert args[0] == self.bot.getnick()
        chanstyle = args[1]
        chan = args[2]
        names = args[3][1:].split()
        for name in names:
            nick = name.lstrip(''.join(umodes.values()))
            self.onjoin(self.getuser(nick), ':'+chan)
            prefixes = name[0:len(name)-len(nick)]
            for p in prefixes:
                self.bot.users[nick].chans[chan].add(p)

    def onerror(self, user, err):
        self.bot.server.disconnect()
        sys.exit(0)

