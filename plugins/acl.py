# acl.py: An acl daemon

import time

from hooks import Hook

botlist = [ "artemis", "botss", "ca", "ChanStat", "doge"
          , "falco", "gnat", "Infobot", "Kuko", "NightBot"
          , "peer", "Sharpie", "shoko", "simbot", "tacobot"
          , "|" ]

throttle = 0

@Hook('PRIVMSG')
def acl_priv(bot, ev):
    if bot.name != "subluminal":
        return ev
    if ev.dest == "#programming" or ev.msg[0] == '[' or ev.user.nick == "***":
        if ev.user.nick in botlist:
            print("PRIVMSG.")
            fixacl(bot)
    return ev

@Hook('JOIN')
def acl_join(bot, ev):
    if bot.name != "subluminal":
        return ev
    if "#programming" in ev.params.split(':', 1)[-1].split():
        if ev.user.nick in botlist+[bot.getnick()]:
            print("JOIN.")
            fixacl(bot)
    return ev

@Hook('NOTICE')
def acl_notc(bot, ev):
    if bot.name != "subluminal":
        return ev
    if ev.dest == "#programming" or ev.msg[0] == '[' or ev.user.nick == "***":
        if ev.user.nick in botlist+[bot.getnick()]:
            print("NOTICE.")
            fixacl(bot)
    return ev

@Hook('NICK')
def acl_nick(bot, ev):
    if bot.name != "subluminal":
        return ev
    if ev.user.nick in botlist or ev.params in botlist:
        print("NICK.")
        fixacl(bot)
    return ev

@Hook('MODE')
def acl_mode(bot, ev):
    if bot.name != "subluminal":
        return ev
    if ev.dest == "#programming" and any(map(lambda t: t[0] in t[1], zip("qaohv", ev.params))):
        if ev.user.nick in botlist:
            print("MODE.")
            fixacl(bot)
    return ev

def fixacl(bot):
    global throttle
    if time.time() - throttle < 10:
        return
    else:
        throttle = time.time()

    try:
        bots = [x.nick for x in bot.chans["#programming"].users() if x.nick in botlist]
        nonbots = [x.nick for x in bot.chans["#programming"].users() if x.nick not in botlist]
    except KeyError:
        bots = nonbots = []
    args = []
    if len(bots) > 0:
        args.append(['+v']+bots)
    if len(nonbots) > 0:
        args.append(['-v']+nonbots)
    bot.mode("#programming", *args)
