# bridge.py: A bridge plugin

import traceback
import time

from hooks import Hook

@Hook("PRIVMSG")
def awflbridge(bot, ev):
    if bot.name == "awfulnet" and ev.msg[0] != '[' and ev.user.nick != "***" and ev.dest[0] == '#':
        t = time.localtime()
        if ev.msg[:8] == "\x01ACTION " and ev.msg[-1] == '\x01':
            msg = ev.msg[8:-1]
            nick = "* "+ev.user.nick
        else:
            msg = ev.msg
            nick = "<"+ev.user.nick+">"
        line = "-%02d:%02d:%02d- [%s] %s %s" %(t.tm_hour, t.tm_min, t.tm_sec, ev.dest, nick, msg)
        bot.ring["subluminal"].privmsg("#awfulnet", line)
    return ev
