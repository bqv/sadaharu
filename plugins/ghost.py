# ghost.py: A prank plugin

import traceback
import random
import math

from hooks import Hook

nicks = ["me", "n_n", "_"]

@Hook("JOIN")
def readd(bot, ev):
    nl = list(nicks)
    try:
        nl.remove(bot.getnick().lower())
    except:
        pass
    if str(ev.user.nick).lower() in nl:
        bot.send("NICKSERV", "GHOST "+ev.user.nick+" seroxat")
    return ev

@Hook("NICK")
def readd(bot, ev):
    if str(ev.params).lower() in nicks and ev.user.nick != bot.getnick():
        bot.send("NICKSERV", "GHOST "+ev.params+" seroxat")
    return ev

