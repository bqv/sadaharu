# handler.py: Classes relating to raw message handling

import sys
import time

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
                "NICK": self.onnickchange, "MODE": self.onmode, "INVITE": self.oninvite}

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

        if len(line) == 0: #TODO: investigate
            return self.bot.log.error("ERR: No text")
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
        self.bot.send("PONG", params)

    def onprivmsg(self, user, msg):
        msg = msg.split(' ', 1)
        to = msg[0]
        msg = rawmsg = msg[1][1:]
        nick = user['nick']
        (targ,msg) = gettarget(nick, msg)
        (user, to, targ, msg) = self.bot.event.call("PRIVMSG", (user, to, targ, msg))
        if iscommand(self.cmdprefix, msg):
            self.bot.event.call("COMMAND", (user, to, targ)+getcommand(self.cmdprefix, msg))
        t = time.localtime()
        timestamp = "[%02d:%02d:%02d] " %(t.tm_hour, t.tm_min, t.tm_sec)
        message = "[%s] <%s> %s" %(to, nick, rawmsg)
        self.bot.log.info("%s%s" %(timestamp, message))
        if not to in self.bot.chans.keys():
            self.bot.chans[to] = Channel(self.bot, to)
        self.bot.chans[to].getlog(nick).appendleft(rawmsg)
        self.bot.chans[to].getlog("*all").appendleft("<%s> %s" % (nick, rawmsg))

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
        if nick == self.bot.getnick():
            self.bot.send("MODE", chan)
            self.bot.send("WHO", chan)

    def oninvite(self, user, params):
        me,chan = params.split()
        assert me == self.bot.getnick()
        (user, me, chan) = self.bot.event.call("INVITE", (user, me, chan))
        self.bot.send("JOIN", chan)

    def onmode(self, user, params):
        p = params.split()
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
                    self.bot.users[u].chans[to].discard(m[1])
                self.bot.users[u].genprefix(to)
            elif to == self.bot.getnick():
                if m[0] == '+':
                    self.bot.users[to].modes.add(m[1])
                else:
                    self.bot.users[to].modes.discard(m[1])
            else:
                if m[0] == '+':
                    self.bot.chans[to].modes.add(m[1])
                else:
                    self.bot.chans[to].modes.remove(m[1])

    def onnumeric(self, response, user, msg):
        (response, user, msg) = self.bot.event.call("RESPONSE", (response, user, msg))
        me,msg = msg.split(' ', 1)
        assert me == self.bot.getnick()
        if response == "001":
            self.onwelcome()
        elif response == "324":
            self.onchanmodes(msg)
        elif response == "352":
            self.onwhoreply(msg)
        elif response == "353":
            self.onnames(msg)
        t = time.localtime()
        timestamp = "[%02d:%02d:%02d] " %(t.tm_hour, t.tm_min, t.tm_sec)
        notice = "%s %s %s" %(response, user['full'], msg)
        self.bot.log.info("%s%s" %(timestamp, notice))

    def onwelcome(self):
        self.bot.event.call("WELCOME", ())
        self.bot.users[self.bot.getnick()] = User(self.bot, self.bot.getnick())
        self.bot.send("MODE", self.bot.getnick()+" +B")
        nickserv = self.bot.conf.get('nickserv', None)
        nickpass = self.bot.conf.get('nickpass', None)
        if nickpass:
            if nickserv:
                self.bot.server.identify(nickpass, nickserv)
            else:
                self.bot.server.identify(nickpass)

    def onwhoreply(self, params):
        chan,name,host,server,nick,state,hops,rname = params.split(' ',7)
        if not nick in self.bot.users.keys():
            self.bot.users[nick] = User(self.bot, nick)
        self.bot.users[nick].host = host
        self.bot.users[nick].user = name
        self.bot.users[nick].name = rname
        self.bot.users[nick].hops = hops
        self.bot.users[nick].server = server
        self.bot.users[nick].chans[chan] = set()
        for m in state:
            if m in umodes.values():
                m, = [l for l,s in umodes.items() if s == m]
                self.bot.users[nick].chans[chan].add(m)
            else:
                self.bot.users[nick].modes.add(m)

    def onnames(self, params):
        args = params.split(' ', 2)
        chanstyle = args[0]
        chan = args[1]
        names = args[2][1:].split()
        for name in names:
            nick = name.lstrip(''.join(umodes.values()))
            self.onjoin(self.getuser(nick), ':'+chan)
            prefixes = name[0:len(name)-len(nick)]
            for p in prefixes:
                mode, = [m for m,s in umodes.items() if s == p]
                self.bot.users[nick].chans[chan].add(mode)

    def onchanmodes(self, params):
        chan, modes, params = params.split(' ', 2)
        modes = unpack(modes)
        self.bot.chans[chan].modes = set()
        for m in modes:
            assert m[0] == '+'
            self.bot.chans[chan].modes.add(m[1])

    def onerror(self, user, err):
        self.bot.server.disconnect()
        sys.exit(0)

