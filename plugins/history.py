# history.py: A history querier

from hooks import Hook

@Hook('COMMAND', commands=['hist'])
def history(bot, ev):
    args = ev.params.split()
    try:
        if args[0].strip().isdigit():
            for msg in reversed(list(bot.chans[ev.dest].getlog('*all'))[0:int(ev.params.strip())]):
                bot.privmsg(ev.user.nick, msg)
            return ev
        if len(args) > 2 or len(args) < 2 or int(args[1]) > 16 or int(args[1]) < 1:
            bot.privmsg(ev.dest, "Too many arguments! Use: "+bot.handler.cmdprefix+ev.cmd+" <num> [nick]")
            return ev
        victim = args[0].lower()
        for msg in reversed(["<" + victim + "> " + x for x in bot.chans[ev.dest].getlog(victim)][0:int(args[1])]):
            bot.privmsg(ev.user.nick, msg)
    except Exception as e:
        bot.privmsg(ev.dest, "Use: "+bot.handler.cmdprefix+ev.cmd+" <num> [nick]")
        raise e
    return ev
