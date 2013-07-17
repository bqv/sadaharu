# sed.py: A substitution plugin

from hooks import Hook

@Hook("PRIVMSG")
def sed(bot, user, to, targ, msg):
    #TODO
    return (user,to,targ,msg)

