# raw.py: A raw command plugin

from hooks import Hook

@Hook("COMMAND", command="raw")
def raw(bot, user, to, targ, cmd, msg):
    bot.server.raw(msg)
    return (user,to,targ,cmd,msg)

