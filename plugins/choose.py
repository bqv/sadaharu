# choose.py: A choice plugin

import math
import random
import traceback

from hooks import Hook

@Hook("PRIVMSG")
def choose(bot, ev):
    if ev.msg[:8] == ".choose ":
        choices = list([x.strip() for x in ev.msg[8:].split(",")])
        if len(choices) < 2:
            return ev
        elif len(choices) == 3:
            if choices[0] in ["yes", "no"]:
                choices += ["maybe", "maybe"]
            if choices[0] in ["Yes", "No"]:
                choices += ["Maybe", "Maybe"]
            if choices[0] in ["YES", "NO"]:
                choices += ["MAYBE", "MAYBE"]
        pick = random.choice(choices)
        if all([len(x)==1 for x in choices]):
            if all([x.isdigit() for x in choices]):
                print("Rolling...")
                pick = str(random.randint(0,9))
            if all([x.isalpha() for x in choices]):
                print("Rolling...")
                pick = chr(97+random.randint(0,25))
        elif len(pick) > 1:
            s = random.randint(1,len(pick)-1)
            brkr = random.choice(["\x02\x02","\x03\x02\x02","\x02\x03\x02","\u200B","\x0F"])
            cnt = math.floor(-math.log(random.random()))
            pick = pick[:s] + brkr*cnt + pick[s:]
            print("Mutated to "+repr(pick))
        bot.privmsg(ev.dest, "%s: \u200B%s" % (ev.user.nick, pick))
    return ev
