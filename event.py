# event.py: Classes relating to events or handling

import sys
import time

class Handler:
    def __init__(self, bot):
        self.bot = bot
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
        msg = msg[1][1:]
        (user, to, msg) = self.bot.event.call("PRIVMSG", (user, to, msg))
        t = time.localtime()
        timestamp = "[%02d:%02d:%02d] " %(t.tm_hour, t.tm_min, t.tm_sec)
        message = "[%s] <%s> %s" %(to, user['nick'], msg)
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
        t = time.localtime()
        timestamp = "[%02d:%02d:%02d] " %(t.tm_hour, t.tm_min, t.tm_sec)
        notice = "%s %s %s" %(response, user['full'], msg)
        self.bot.log.info("%s%s" %(timestamp, notice))

    def onerror(self, user, err):
        self.bot.server.disconnect()
        sys.exit(0)

class Events:
    class HookObj:
        def __init__(self, name, args):
            self.name = name
            self.nargs = args
            self._active = {0:[], 1:[], 2:[], 3:[]}
            self._inactive = {0:[], 1:[], 2:[], 3:[]}

        def add(self, thook, priority=1, disabled=False):
            if disabled:
                self._inactive[priority].append(thook)
            else:
                self._active[priority].append(thook)

        def remove(self, name, priority=1, disabled=False):
            if disabled:
                for i,thook in enumerate(self._inactive[priority]):
                    if thook.name == name:
                        self._inactive.remove(i)
            else:
                for i,thook in enumerate(self._active[priority]):
                    if thook.name == name:
                        self._active.remove(i)

        def _get(self, priority, with_disabled=False):
            l = self._active[priority]
            if with_disabled:
                l += self._inactive[priority]
            return l

        def active(self):
            l = []
            map(l.extend, self._active.values()[::-1])
            return l

        def inactive(self):
            l = []
            map(l.extend, self._inactive.values()[::-1])
            return l

        def low(self, with_disabled=False):
            return self._get(0, with_disabled)
        def mid(self, with_disabled=False):
            return self._get(1, with_disabled)
        def high(self, with_disabled=False):
            return self._get(2, with_disabled)
        def urgent(self, with_disabled=False):
            return self._get(3, with_disabled)

    hooks = {"SEND":HookObj("SEND",2), "SENDRAW":HookObj("SENDRAW",1), "READ":HookObj("READ",3),
            "READRAW":HookObj("READRAW",1), "PING":HookObj("PING",1), "PONG":HookObj("PONG",1),
            "PRIVMSG":HookObj("PRIVMSG",3), "NICK":HookObj("NICK",1), "NOTICE":HookObj("NOTICE",2),
            "RESPONSE":HookObj("RESPONSE",3)}

    def __init__(self, bot):
        self.bot = bot

    def call(self, evname, args=()):
        args = self.runhooks(self.hooks[evname].urgent(), evname, args)
        args = self.runhooks(self.hooks[evname].high(), evname, args)
        args = self.runhooks(self.hooks[evname].mid(), evname, args)
        args = self.runhooks(self.hooks[evname].low(), evname, args)
        return args

    def runhooks(self, hookset, evname, args):
        for hook in hookset:
            result = hook(args)
            if result:
                if len(result) == self.hooks[evname].nargs:
                    args = result
                else:
                    self.bot.log.error("Bad return value from hook %s", str(hook))
            else:
                raise CancelEvent(hook.name)
        return args
    
class CancelEvent(Exception):
    pass

