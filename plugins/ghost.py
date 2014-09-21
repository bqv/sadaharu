# ghost.py: A prank plugin

import traceback
import random
import math

from hooks import Hook

@Hook("JOIN")
def readd(bot, ev):
    nicks = list(bot.conf.get('protected', []))
    try:
        nicks.remove(bot.getnick().lower())
    except:
        pass
    if str(ev.user.nick).lower() in nicks:
        bot.send("NICKSERV", "GHOST "+ev.user.nick+" seroxat")
    return ev

@Hook("NICK")
def readd(bot, ev):
    if str(ev.params).lower() in bot.conf.get('protected', []) and ev.user.nick != bot.getnick():
        bot.send("NICKSERV", "GHOST "+ev.params+" seroxat")
    return ev

