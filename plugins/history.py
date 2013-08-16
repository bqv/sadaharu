# history.py: A history querier

from hooks import Hook

@Hook('COMMAND', commands=['hist'])
def history(bot, user, chan, targ, cmd, msg):
    nick = user['nick']
    args = msg.split()
    try:
        if args[0].strip().isdigit():
            for msg in reversed(list(bot.chans[chan].getlog('*all'))[0:int(msg.strip())]):
                bot.privmsg(nick, msg)
            return (user, chan, targ, cmd, msg)
        if len(args) > 2 or len(args) < 2 or int(args[1]) > 16 or int(args[1]) < 1:
            bot.privmsg(chan, "Too many arguments! Use: !history <num> [nick]")
            return (user, chan, targ, cmd, msg)
        victim = args[0].lower()
        for msg in reversed(["<" + victim + "> " + x for x in bot.chans[chan].getlog(victim)][0:int(args[1])]):
            bot.privmsg(nick, msg)
    except Exception as e:
        bot.privmsg(chan, str(e))
        bot.privmsg(chan, "Use: !history <num> [nick]")
    return (user, chan, targ, cmd, msg)
