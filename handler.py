# handler.py: Classes relating to raw message handling

import sys
import time
import traceback

from event import EventCancelled, AbstractEvent, AbstractUserEvent, UserOperationEvent, DirectedOperationEvent
from static import *
from chan import Channel
from user import User

class Handler:
    def __init__(self, bot):
        self.bot = bot
        self.cmdprefix = bot.conf['prefix']
        self.registered = {"PING": self.onping, "PRIVMSG": self.onprivmsg,
                "NOTICE": self.onnotice, "ERROR": self.onerror, "JOIN": self.onjoin,
                "NICK": self.onnickchange, "MODE": self.onmode, "INVITE": self.oninvite,
                "QUIT": self.onquit, "PART": self.onpart}

    def handle(self, line):
        if not line:
            return

        self.bot.log.debug("[%s] "%(self.bot.name,)+line)

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

        user = User(prefix)

        class ReadEvent(UserOperationEvent):
            name = "READ"
            def __init__(self, user, oper, params):
                UserOperationEvent.__init__(self, user, params)
                self.oper = oper

        try:
            rev = ReadEvent(user, command, params).fire(self.bot)

            if rev.oper in self.registered.keys():
                self.registered[rev.oper](rev.user, rev.params)
            elif len(rev.oper) == 3 and rev.oper.isdigit():
                self.onnumeric(rev.oper, rev.user, rev.params)
            else:
                self.bot.log.warning("Couldn't process unregistered command: %s %s", rev.oper, rev.params)
        except EventCancelled:
            return

    def onping(self, user, msg):
        class PingEvent(UserOperationEvent):
            name = "PING"
        stamp = PingEvent(user, msg).fire(self.bot).params
        self.bot.send("PONG", stamp)

    def onprivmsg(self, user, msg):
        pfx = self.cmdprefix
        class PrivmsgEvent(DirectedOperationEvent):
            name = "PRIVMSG"
        class CommandEvent(AbstractEvent):
            name = "COMMAND"
            def __init__(self, pev):
                AbstractEvent.__init__(self)
                self.user = pev.user
                self.dest = pev.dest
                self._msg = pev._msg
                l = pev.msg.lstrip()[len(pfx):].split(' ', 1)
                if len(l) == 2:
                    self.cmd = l[0]
                    self.params = l[1]
                else:
                    self.cmd = l[0]
                    self.params = ""
            def fire(self, bot):
                print(self.cmd)
                AbstractEvent.fire(self, bot)
        pev = PrivmsgEvent(user, msg).fire(self.bot)
        if pev.msg.lstrip().startswith(self.cmdprefix):
            cev = CommandEvent(pev).fire(self.bot)
        rcolors = [19, 20, 22, 24, 25, 26, 27, 28, 29]
        nc = rcolors[sum(ord(i) for i in pev.user.nick) % 9] - 16
        nick = "\x03%d%s\x03" %(nc, pev.user.nick)
        self.log("[%s] <%s> %s" %(pev.dest, nick, pev.msg))
        if not pev.dest in self.bot.chans.keys():
            self.bot.chans[pev.dest] = Channel(self.bot, pev.dest)
        self.bot.chans[pev.dest].getlog(pev.user.nick).appendleft(pev.msg)
        self.bot.chans[pev.dest].getlog().appendleft("<%s> %s" % (pev.user.nick, pev.msg))

    def onnotice(self, user, msg):
        class NoticeEvent(DirectedOperationEvent):
            name = "NOTICE"
        nev = NoticeEvent(user, msg).fire(self.bot)
        self.log("[%s] -%s- %s" %(nev.dest, nev.user.nick, nev.msg))

    def onnickchange(self, user, msg):
        class NickEvent(UserOperationEvent):
            name = "NICK"
        nev = NickEvent(user, msg.split(':',1)[-1]).fire(self.bot)
        if nev.user.nick == self.bot.getnick():
            self.bot.server.nick = nev.params
        else:
            try:
                self.bot.users[nev.params] = self.bot.users.pop(nev.user.nick)
            except:
                pass

    def onjoin(self, user, msg):
        class JoinEvent(UserOperationEvent):
            name = "JOIN"
        jev = JoinEvent(user, msg).fire(self.bot)
        if not jev.params in self.bot.chans.keys():
            self.bot.chans[jev.params] = Channel(self.bot, jev.params)
        if not jev.user.nick in self.bot.users.keys():
            self.bot.users[jev.user.nick] = jev.user
        self.bot.users[jev.user.nick].chans[jev.params] = set()
        if jev.user.nick == self.bot.getnick():
            self.bot.send("MODE", jev.params)
            self.bot.send("WHO", jev.params)

    def onpart(self, user, msg):
        class PartEvent(DirectedOperationEvent):
            name = "PART"
        pev = PartEvent(user, msg).fire(self.bot)
        if not pev.dest in self.bot.chans.keys():
            self.bot.chans[pev.dest] = Channel(self.bot, pev.dest)
        if not pev.user.nick in self.bot.users.keys():
            self.bot.users[pev.user.nick] = User(pev.user.nick)
        try:
            self.bot.users[pev.user.nick].chans.pop(pev.dest)
            if pev.user.nick == self.bot.getnick():
                self.bot.chans.pop(pev.dest)
        except KeyError:
            pass

    def onquit(self, user, msg):
        class QuitEvent(DirectedOperationEvent):
            name = "QUIT"
        qev = QuitEvent(user, msg).fire(self.bot)
        if not qev.dest in self.bot.chans.keys():
            self.bot.chans[qev.dest] = Channel(self.bot, qev.dest)
        try:
            self.bot.users.pop(qev.user.nick)
            if qev.user.nick == self.bot.getnick():
                self.bot.quit()
        except KeyError:
            pass

    def oninvite(self, user, msg):
        class InviteEvent(DirectedOperationEvent):
            name = "INVITE"
        iev = InviteEvent(user, msg).fire(self.bot)
        if iev.dest == self.bot.getnick():
            self.bot.send("JOIN", iev._msg)

    def onmode(self, user, msg):
        class ModeEvent(DirectedOperationEvent):
            name = "MODE"
        mev = ModeEvent(user, msg).fire(self.bot)
        try: #TODO: fix...
            p = mev._msg.split()
            modes = unpack(p[0].lstrip(':'))
            users = p[1:]
            for m in modes:
                try:
                    if m[1] in umodes:
                        u = users.pop(0)
                        if m[0] == '+':
                            self.bot.users[u].chans[mev.dest].add(m[1])
                        else:
                            self.bot.users[u].chans[mev.dest].discard(m[1])
                        self.bot.users[u].genprefix(mev.dest)
                    elif mev.dest == self.bot.getnick():
                        if m[0] == '+':
                            try:
                                self.bot.users[mev.dest].modes.add(m[1])
                            except: pass
                        else:
                            self.bot.users[mev.dest].modes.discard(m[1])
                    else:
                        if m[0] == '+':
                            try:
                                self.bot.chans[mev.dest].modes.add(m[1])
                            except: pass
                        else:
                            self.bot.chans[mev.dest].modes.remove(m[1])
                except:
                    pass
        except:
            traceback.print_exc()

    def onnumeric(self, response, user, msg):
        getnick = self.bot.getnick
        class NumericEvent(AbstractUserEvent):
            name = "RESPONSE"
            def __init__(self, user, num, msg):
                AbstractUserEvent.__init__(self, user)
                self.oper = int(num)
                me,arg = msg.split(' ', 1)
                #assert me == getnick()
                self.arg = arg
        nev = NumericEvent(user, response, msg).fire(self.bot)
        if nev.oper == 1:
            self.onwelcome(nev)
        elif nev.oper == 324:
            self.onchanmodes(nev)
        elif nev.oper == 352:
            self.onwhoreply(nev)
        elif nev.oper == 353:
            self.onnames(nev)
        self.log("%s %s %s" %(nev.oper, nev.user.hostmask, nev.arg))

    def onwelcome(self, ev):
        class WelcomeEvent(AbstractEvent):
            name = "WELCOME"
        WelcomeEvent().fire(self.bot)
        self.bot.users[self.bot.getnick()] = User(self.bot.getnick())
        self.bot.send("MODE", self.bot.getnick()+" +B")
        nickserv = self.bot.conf.get('nickserv', None)
        nickpass = self.bot.conf.get('nickpass', None)
        if nickpass:
            if nickserv:
                self.bot.server.identify(nickpass, nickserv)
            else:
                self.bot.server.identify(nickpass)

    def onwhoreply(self, ev):
        chan,name,host,server,nick,state,hops,rname = ev.arg.split(' ',7)
        if not nick in self.bot.users.keys():
            self.bot.users[nick] = User(nick)
        self.bot.users[nick].host = host
        self.bot.users[nick].user = name
        self.bot.users[nick].name = rname
        self.bot.users[nick].hops = hops
        self.bot.users[nick].server = server
        self.bot.users[nick].chans[chan] = set()
        try:
            for m in state:
                if m in umodes.values():
                    m, = [l for l,s in umodes.items() if s == m]
                    self.bot.users[nick].chans[chan].add(m)
                else:
                    self.bot.users[nick].modes.add(m)
        except:
            pass

    def onnames(self, ev):
        args = ev.arg.split(' ', 2)
        chanstyle = args[0]
        chan = args[1]
        names = args[2][1:].split()
        for name in names:
            nick = name.lstrip(''.join(umodes.values()))
            self.onjoin(User(nick), ':'+chan)
            prefixes = name[0:len(name)-len(nick)]
            for p in prefixes:
                mode, = [m for m,s in umodes.items() if s == p]
                try:
                    self.bot.users[nick].chans[chan].add(mode)
                except:
                    pass #TODO:fix

    def onchanmodes(self, ev):
        try:
            print(ev.arg)
            try:
                chan, modes, params = ev.arg.split(' ', 2)
            except ValueError:
                chan, modes = ev.arg.split(' ', 1)
            modes = unpack(modes)
            self.bot.chans[chan].modes = set()
            for m in modes:
                assert m[0] == '+'
                self.bot.chans[chan].modes.add(m[1])
        except:
            pass

    def onerror(self, user, err):
        self.bot.server.disconnect()
        sys.exit(0)

    def log(self, message):
        t = time.localtime()
        timestamp = "[%02d:%02d:%02d]" %(t.tm_hour, t.tm_min, t.tm_sec)
        self.bot.log.info("%s [%s] %s" %(timestamp, self.bot.name, message))

