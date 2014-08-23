# bridge.py: A bridge plugin

import traceback
import time

from hooks import Hook

@Hook("PRIVMSG")
def awflbridge(bot, user, to, targ, msg):
    nick = user['nick']
    if bot.name == "awfulnet" and msg[0] != '[':
        t = time.localtime()
        line = "-%02d:%02d:%02d- [%s] <%s> %s" %(t.tm_hour, t.tm_min, t.tm_sec, to, nick, msg)
        bot.ring["subluminal"].privmsg("#awfulnet", line)
    return (user,to,targ,msg)
