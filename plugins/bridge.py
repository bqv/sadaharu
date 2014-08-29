# bridge.py: A bridge plugin

import traceback
import time

from hooks import Hook

@Hook("PRIVMSG")
def awflbridge(bot, ev):
    if bot.name == "awfulnet" and ev.msg[0] != '[' and ev.dest[0] == '#':
        t = time.localtime()
        line = "-%02d:%02d:%02d- [%s] <%s> %s" %(t.tm_hour, t.tm_min, t.tm_sec, ev.dest, ev.user.nick, ev.msg)
        bot.ring["subluminal"].privmsg("#awfulnet", line)
    return ev
