# lol.py: A test plugin

from hooks import Hook

@Hook("PRIVMSG", disabled=True)
def lol_per_msg(args):
    (user, to, msg) = args
    i = LOL()
    msg = msg[::-1]
    return (user, to, msg)

class LOL:
    def __init__(self):
        print("LOL")
