# lol.py: A test plugin

from hooks import Hook

@Hook("COMMAND", disabled=False, command="printlol")
def lol_per_msg(bot, user, to, targ, cmd, msg):
    i = LOL()

class LOL:
    def __init__(self):
        print("LOL")
