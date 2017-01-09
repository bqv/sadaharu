# earl.py: Plugin for rewriting earl relay lines

import re

from hooks import Hook
from user import User

RE = re.compile(r"\[([^:\]]+)\] (.*)")

@Hook("PRIVMSG")
def relaymsg(bot, ev):
    match = RE.match(ev.msg)
    if match:
        user = User(match.group(1)+"!earl@rewrite")
        msg = ev.dest+" :"+match.group(2)
        bot.handler.onprivmsg(user, msg)
        #return None
    return ev

