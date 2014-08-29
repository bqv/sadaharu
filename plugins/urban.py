# urban.py: An urbandictionary querier

from hooks import Hook
import requests
import traceback
import random


@Hook('COMMAND', commands=["urbandictionary", "urban"])
def ud(bot, ev):
    if not ev.params:
        bot.privmsg(ev.dest, "Usage: ud <phrase> [index]")
        return ev

    url = 'http://www.urbandictionary.com/iphone/search/define'
    args = ev.params.split()
    params = {'term': ' '.join(args[:-1])}
    index = 0
    try:
        index = int(args[-1]) - 1
    except ValueError:
        params = {'term': ev.params}
    if len(args) == 1:
        params = {'term': ev.params}
        index = 0
    request = requests.get(url, params=params)

    data = request.json()
    defs = None
    output = ""
    try:
        defs = data['list']

        if data['result_type'] == 'no_results':
            bot.privmsg(ev.dest, failmsg() % (ev.user.nick, params['term']))
            return None

        output = defs[index]['word'] + ' [' + str(index+1) + ']: ' + defs[index]['definition']
    except:
        traceback.print_exc()
        bot.privmsg(ev.dest, failmsg() % (ev.user.nick, params['term']))
        return None

    output = output.strip()
    output = output.rstrip()
    output = ' '.join(output.split())

    bot.privmsg(ev.dest, "%s: %s" % (ev.user.nick, output))
    return ev

def failmsg():
    return random.choice([
        "%s: No definition found for %s.",
        "%s: The heck is '%s'?!",
        "%s: %s. wut.",
        "%s: %s? I dunno...",
        "%s: Stop searching weird things. What even is '%s'?",
        "%s: Computer says no. '%s' not found.",
        "*sigh* someone tell %s what '%s' means",
        "%s: This is a family channel. Don't look up '%s'",
        "%s: Trust me, you don't want to know what '%s' means.",
        "%s: %s [1]: Something looked up by n00bs.",
        "%s: %s [1]: An obscure type of fish.",
        "No %s, no '%s' for you.",
        "Shh %s, nobody's meant to know about '%s'...",
        "Really %s? %s?"])

@Hook('COMMAND', commands=["urbandictionaryrandom", "urbanrandom"])
def udr(bot, ev):
    ''' Random UrbanDictionary lookup. '''
    word = requests.get("http://api.urbandictionary.com/v0/random").json()['list'][0]['word']
    ev.params = word
    return ud(bot, ev)
