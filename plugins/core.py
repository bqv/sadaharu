# core.py: Plugin for core functions

from hooks import Hook

@Hook("COMMAND")
def raw(bot, user, to, targ, cmd, msg):
    bot.server.raw(msg)
    return (user,to,targ,cmd,msg)

@Hook("COMMAND", commands=["exec"])
def py(bot, user, to, targ, cmd, msg):
    try:
        output = eval(msg, globals(), locals())
        if output is not None:
            bot.privmsg(to, output)
    except (NameError, SyntaxError):
        exec(msg, locals())
    return (user,to,targ,cmd,msg)

@Hook("COMMAND")
def privmsg(bot, user, to, targ, cmd, msg):
    bot.send("PRIVMSG", msg)
    return (user,to,targ,cmd,msg)

@Hook("COMMAND")
def part(bot, user, to, targ, cmd, msg):
    bot.send("PART", msg)
    return (user,to,targ,cmd,msg)

@Hook("COMMAND")
def quit(bot, user, to, targ, cmd, msg):
    bot.send("QUIT", msg)
    return (user,to,targ,cmd,msg)

@Hook("SENDRAW")
def onraw(bot, line):
    print("=> "+line)
    return (line,)
