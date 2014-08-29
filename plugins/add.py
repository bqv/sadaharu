# add.py: A copycat plugin

import traceback
import random
import math

from hooks import Hook

@Hook("PRIVMSG")
def readd(bot, ev):
    if ev.msg[:4] == ".add" and ev.user.nick != bot.getnick():
        import time
        time.sleep(1.5)
        for i in range(math.floor(-math.log(random.random())/math.log(2))):
            bot.privmsg(ev.dest, ".add")
    return ev

