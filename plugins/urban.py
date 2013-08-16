# urban.py: An urbandictionary querier

from hooks import Hook
import requests
import traceback
import random


@Hook('COMMAND', commands=["urbandictionary", "urban"])
def ud(bot, user, to, targ, cmd, msg):
    if not msg:
        bot.privmsg(to, "Usage: ud <phrase> [index]")
        return (user, to, targ, cmd, msg)

    url = 'http://www.urbandictionary.com/iphone/search/define'
    args = msg.split()
    params = {'term': ' '.join(args[:-1])}
    index = 0
    try:
        index = int(args[-1]) - 1
    except ValueError:
        params = {'term': msg}
    if len(args) == 1:
        params = {'term': msg}
        index = 0
    request = requests.get(url, params=params)

    data = request.json()
    defs = None
    output = ""
    try:
        defs = data['list']

        if data['result_type'] == 'no_results':
            bot.privmsg(to, failmsg() % (user, params['term']))
            return None

        output = defs[index]['word'] + ' [' + str(index+1) + ']: ' + defs[index]['definition']
    except:
        traceback.print_exc()
        bot._msg(to, failmsg() % (user, params['term']))
        return None

    output = output.strip()
    output = output.rstrip()
    output = ' '.join(output.split())

    if len(output) > 300:
        tinyurl = bot.state.data['shortener'](bot, defs[index]['permalink'])
        output = output[:output.rfind(' ', 0, 170)] + '... [Read more: %s]' % (tinyurl)
        bot.privmsg(to, "%s: %s" % (user, output))

    else:
        bot.privmsg(to, "%s: %s" % (user['nick'], output))
    return (user, to, targ, cmd, msg)

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
def udr(bot, user, to, targ, cmd, msg):
    ''' Random UrbanDictionary lookup. '''
    word = requests.get("http://api.urbandictionary.com/v0/random").json()['list'][0]['word']
    return ud(bot, user, to, targ, cmd, msg)
