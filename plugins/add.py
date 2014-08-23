# add.py: A copycat plugin

import traceback
import random
import math

from hooks import Hook

@Hook("PRIVMSG")
def readd(bot, user, to, targ, msg):
    nick = user['nick']

    if msg[:4] == ".add" and nick != bot.getnick():
        import time
        time.sleep(1.5)
        for i in range(math.floor(-math.log(random.random())/math.log(2))):
            bot.privmsg(to, ".add")
    return (user,to,targ,msg)

