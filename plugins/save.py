# save.py: A history saver

from hooks import Hook

from paste import ix as paste

@Hook('COMMAND', commands=['log'])
def save(bot, ev):
    args = ev.params.split()
    try:
        if args[0].strip().isdigit():
            lines = '\n'.join(reversed(list(bot.chans[ev.dest].getlog())[0:int(ev.params.strip())]))
        else:
            if len(args) > 2 or len(args) < 2 or int(args[1]) > 16 or int(args[1]) < 1:
                bot.reply(ev.dest, "Too many arguments! Use: "+ev.cmd+" [nick] <num>")
                return ev
            victim = args[0].lower()
            lines = '\n'.join(reversed(["<" + victim + "> " + x for x in bot.chans[ev.dest].getlog(victim)][0:int(args[1])]))
        link = paste(lines)
        print(link)
        if link:
            bot.reply(ev.dest, ev.user.nick+": "+link+".txt")
        else:
            bot.reply(ev.dest, "\x02[;_;]\x02 Failed to paste!")
    except Exception as e:
        bot.privmsg(ev.dest, "Use: "+ev.cmd+" [nick] <num>")
        print(e)
    return ev

