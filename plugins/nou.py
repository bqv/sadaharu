# nou.py: A copycat plugin

import traceback
import random
import math

from hooks import Hook

@Hook("PRIVMSG")
def nou(bot, ev):
    if ev.msg.lower().strip().rstrip('!').strip() == "no u" and ev.user.nick != bot.getnick():
        import time
        time.sleep(1.5)
        bot.privmsg(ev.dest, "no u")
    return ev

