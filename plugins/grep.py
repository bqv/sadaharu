# grep.py: A channel history grepper

import re

from hooks import Hook

@Hook('COMMAND', commands=['find', 'regex'])
def grep(bot, ev):
    try:
        regex = re.compile(ev.params)
    except Exception as e:
        bot.privmsg(ev.dest, "\x02Bad Regex\x02 "+ev.params)
        raise e
    matches = []
    for msg in bot.chans[ev.dest].getlog('*all'):
        if regex.search(msg):
            matches.insert(0, msg)
    for fire in reversed(matches[-3:]):
        bot.privmsg(ev.dest, fire)
    if len(matches) > 3:
        bot.privmsg(ev.dest, "[...] and %d earlier messages" %(len(matches)-3,))
    return ev
