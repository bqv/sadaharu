# choose.py: A choice plugin

import random
import traceback

from hooks import Hook

@Hook("PRIVMSG")
def choose(bot, user, to, targ, msg):
    nick = user['nick']

    if msg[:8] == ".choose ":
        choices = msg[8:].split(",")
        if len(choices) == 0:
            return (user,to,targ,msg)
        pick = random.choice(choices)
        bot.privmsg(to, "%s: %s" % (nick, pick.strip()))
    return (user,to,targ,msg)
