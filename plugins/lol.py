# lol.py: A test plugin

from sadaharu import Hook

@Hook("PRIVMSG")
def lol_per_msg(args):
    (user, to, msg) = args
    i = LOL()
    msg = msg[::-1]
    return (user, to, msg)

class LOL:
    def __init__(self):
        print("LOL")
