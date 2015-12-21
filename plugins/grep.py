# grep.py: A channel history grepper

import re

from hooks import Hook

@Hook('COMMAND', commands=['find', 'regex'])
def grep(bot, ev):
    try:
        regex = re.compile(ev.params)
    except Exception as e:
        bot.notice(ev.dest, "\x02Bad Regex\x02 "+ev.params)
        raise e
    for line in search(bot.chans[ev.dest].getlog(), regex):
        bot.notice(ev.dest, line)
    return ev

@Hook('COMMAND', commands=['ifind', 'iregex'])
def igrep(bot, ev):
    try:
        regex = re.compile(ev.params, re.I)
    except Exception as e:
        bot.notice(ev.dest, "\x02Bad Regex\x02 "+ev.params)
        raise e
    for line in search(bot.chans[ev.dest].getlog(), regex, False):
        bot.notice(ev.dest, line)
    return ev

def search(log, regex, case=True):
    matches = []
    for msg in log:
        if regex.search(msg):
            matches.insert(0, msg)
    for fire in reversed(matches[-3:]):
        yield fire
    if len(matches) > 3:
        yield "[...] and %d earlier messages" %(len(matches)-3,)
