# add.py: A copycat plugin

import traceback
import random
import math
import re

from hooks import Hook

@Hook("PRIVMSG")
def readd(bot, ev):
    if bot.name != "subluminal" or ev.dest not in ["#maths"] or ev.msg[0] == '[' or ev.user.nick == "***":
        return ev
    if ev.user.nick != bot.getnick():
        match = re.search(r"\b[mM][aA][tT][hH]\b", ev.msg)
        if match:
            text = match.group(0)
            if "\x02" in ev.msg:
                s = "\x01ACTION \x02%s%s%s%s\x02\x01"
            else:
                s = "\x01ACTION %s%s%s%s\x01"
            s %= ("H" if text[0] == "M" else "h","%s","%s","%s")
            s %= ("I" if text[1] == "A" else "i","%s","%s")
            s %= ("SS" if text[2] == "T" else "ss","%s")
            s %= ("ES" if text[3] == "H" else "es",)
            bot.privmsg(ev.dest, s)
    return ev

@Hook("SEND")
def math(bot, ev):
    if ev.params and 'math' in ev.params:
        return False
    return ev
