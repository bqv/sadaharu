# add.py: A copycat plugin

import traceback
import random
import math

from hooks import Hook

@Hook("PRIVMSG")
def readd(bot, ev):
    return ev
    if bot.name != "subluminal":
        return ev
    if ev.msg[:4] == ".add" and ev.user.nick != bot.getnick():
        import time
        time.sleep(1.5)
        for i in range(math.floor(-math.log(random.random()))):
            bot.privmsg("|", ".add")
    return ev

