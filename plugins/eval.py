# eval.py: A python interpreter plugin

from hooks import Hook

@Hook("COMMAND", command="exec")
def execpy(bot, user, to, targ, cmd, msg):
    try:
        output = eval(msg, globals(), locals())
        if output is not None:
            bot.privmsg(to, output)
    except (NameError, SyntaxError):
        exec(msg, locals())
    return (user,to,targ,cmd,msg)

