# handler.py: Classes relating to raw message handling

import sys
import time

from event import CancelEvent
from parsing import *

class Handler:
    def __init__(self, bot):
        self.bot = bot
        self.cmdprefix = bot.conf['prefix']
        self.registered = {"PING": self.onping, "PRIVMSG": self.onprivmsg,
                "NOTICE": self.onnotice, "ERROR": self.onerror}

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
                host = prefix
                nick = user = ""
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
        self.bot.server.nick = newnick

    def onnumeric(self, response, user, msg):
        (response, user, msg) = self.bot.event.call("RESPONSE", (response, user, msg))
        if response == "376":
            self.onwelcome()
        t = time.localtime()
        timestamp = "[%02d:%02d:%02d] " %(t.tm_hour, t.tm_min, t.tm_sec)
        notice = "%s %s %s" %(response, user['full'], msg)
        self.bot.log.info("%s%s" %(timestamp, notice))

    def onwelcome(self):
        self.bot.event.call("WELCOME", ())
        self.bot.server.send("MODE", self.bot.server.nick+" +B")
        nickserv = self.bot.conf.get('nickserv', None)
        nickpass = self.bot.conf.get('nickpass', None)
        if nickpass:
            if nickserv:
                self.bot.server.identify(nickpass, nickserv)
            else:
                self.bot.server.identify(nickpass)

    def onerror(self, user, err):
        self.bot.server.disconnect()
        sys.exit(0)

