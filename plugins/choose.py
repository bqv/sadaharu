# choose.py: A choice plugin

import random
import traceback

from hooks import Hook

@Hook("PRIVMSG")
def choose(bot, ev):
    if ev.msg[:8] == ".choose ":
        choices = list([x.strip() for x in ev.msg[8:].split(",")])
        if len(choices) < 2:
            return ev
        pick = random.choice(choices)
        if all([len(x)==1 for x in choices]):
            if all([x.isdigit() for x in choices]):
                print("Rolling...")
                pick = str(random.randint(0,9))
            if all([x.isalpha() for x in choices]):
                print("Rolling...")
                pick = chr(97+random.randint(0,25))
        bot.privmsg(ev.dest, "%s: \u200B%s" % (ev.user.nick, pick))
    return ev
