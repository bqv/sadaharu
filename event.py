# event.py: Event handler class

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

        (command, user, params) = self.bot.event.call("READ", (command, user, params))

        if command in self.registered.keys():
            self.registered[command](user, params)
        elif len(command) == 3 and command.isdigit():
            self.onnumeric(command, user, params)
        else:
            self.bot.log.warning("Couldn't process unregistered command: %s %s", command, params)

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
        (user, msg) = self.bot.event.call("PRIVMSG", (user, msg))
        t = time.localtime()
        timestamp = "[%02d:%02d:%02d] " %(t.tm_hour, t.tm_min, t.tm_sec)
        msg = msg.split(' ', 1)
        to = msg[0]
        msg = msg[1][1:]
        message = "[%s] <%s> %s" %(to, user['nick'], msg)
        self.bot.log.info("%s%s" %(timestamp, message))

    def onnotice(self, user, msg):
        (user, msg) = self.bot.event.call("NOTICE", (user, msg))
        t = time.localtime()
        timestamp = "[%02d:%02d:%02d] " %(t.tm_hour, t.tm_min, t.tm_sec)
        msg = msg.split(' ', 1)
        to = msg[0]
        msg = msg[1][1:]
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

class Events:
    def __init__(self, bot):
        self.bot = bot
        self.hooks = {"SEND": [2], "SENDRAW": [1], "READ": [3], "READRAW": [1],
                "PING": [1], "PONG": [1], "PRIVMSG": [2], "NICK": [1], "NOTICE": [2],
                "RESPONSE": [3]}

    def call(self, evname, args=()):
        for hook in self.hooks[evname][1:]:
            result = hook(args)
            if result:
                if len(result) == self.hooks[evname][0]:
                    args = result
                else:
                    self.bot.log.error("Bad return value from hook %s", str(hook))
        return args
