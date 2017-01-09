# core.py: Plugin for core functions

import os
import sys
import code
import functools
import threading
import subprocess

from hooks import Hook

class IRCterpreter(code.InteractiveConsole):
    def __init__(self, localVars, bot):
        self.bot = bot
        self.curnick = ""
        self.curchan = ""
        self.buff = []
        code.InteractiveConsole.__init__(self, localVars)

    def write(self, data):
        self.buff.append(data)

    def flush(self):
        pass

    def flushbuf(self):
        out = ''.join(self.buff).rstrip('\n').replace("\n\n", "\n \n")

        if 'File "<console>", line 1' in out:
            print(out)
            out = '\x02[;_;]\x02 '+out[out.rfind("\n")+1:]

        if len(out) > 0:
            self.bot.reply(self.curchan, out)
        self.buff = []

    def run(self, nick, chan, code):
        if not 'self' in self.locals.keys():
            self.locals['self'] = self
        self.curnick = nick
        self.curchan = chan
        sys.stdout = sys.interp = self
        self.push(code)
        sys.stdout = sys.__stdout__
        self.flushbuf()

@Hook("COMMAND", scope=1)
def raw(bot, ev):
    line = bytes(ev.params, "utf-8").decode("unicode_escape")
    bot.server.raw(line)
    return ev

@Hook("COMMAND", commands=["exec"], scope=1)
def py(bot, ev):
    ipring = bot.data.get("interp", None)
    if not ipring:
        bot.data["interp"] = ipring = {'env': locals()}
        ipring['env'].update(globals())
        ipring['env'].update({'bot': bot})
        ipring['env'].update({'say': lambda x: bot.privmsg(ev.dest, x)})
        ipring['env'].update({'notice': lambda x: bot.notice(ev.dest, x)})
    ip = ipring.get(ev.user.nick, None)
    if not ip:
        ipring[ev.user.nick] = ip = IRCterpreter(ipring['env'], bot)
    ip.run(ev.user.nick, ev.dest, ev.params)
    return ev

@Hook("COMMAND", commands=["bash", "sh"], scope=1)
def shell(bot, ev):
    threading.Thread(target=runprocess, args=[bot, ev, True]).start()
    return ev
@Hook("COMMAND", commands=["rsh"], scope=1)
def rawshell(bot, ev):
    threading.Thread(target=runprocess, args=[bot, ev, False]).start()
    return ev

def runprocess(bot, ev, restrict=False):
    cmd = ev.params.lstrip()
    print("Running: "+cmd)
    with subprocess.Popen(["bash","-c",cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as p:
        counter = 3
        for line in iter(p.stdout.readline, b''):
            if restrict and counter == 0:
                bot.reply(ev.dest, "\x02[?_?]\x02 Quelling further output from command: "+cmd)
                return
            else:
                counter -= 1
                bot.reply(ev.dest, line.decode('utf8').rstrip())
        print("Process returned: %d"%(p.wait(),))

@Hook("PRIVMSG")
def short(bot, ev):
    if ev.msg[:4] == ">>> ":
        if ev.user.nick in bot.conf.get("wheel", []):
            ev.params = ev.msg[4:]
            ev.cmd = ">>>"
            py(bot, ev)
        else:
            print("Access denied for "+ev.user.nick)
        return ev
    if ev.msg[:3] == ":: ":
        if ev.user.nick in bot.conf.get("wheel", []):
            ev.params = ev.msg[3:]
            ev.cmd = "::"
            raw(bot, ev)
        else:
            print("Access denied for "+ev.user.nick)
        return ev
    if ev.msg[:2] == "$ ":
        if ev.user.nick in bot.conf.get("wheel", []):
            ev.params = ev.msg[2:]
            ev.cmd = "$"
            shell(bot, ev)
        else:
            print("Access denied for "+ev.user.nick)
        return ev
    if ev.msg[:1] == "%":
        if ev.user.nick in bot.conf.get("wheel", []):
            ev.params = ev.msg[1:]
            ev.cmd = "%"
            rawshell(bot, ev)
        else:
            print("Access denied for "+ev.user.nick)
        return ev
    return ev

@Hook("COMMAND", scope=1)
def say(bot, ev):
    line = bytes(ev.params, "utf-8").decode("unicode_escape")
    bot.privmsg(ev.dest, line)
    return ev

@Hook("COMMAND", scope=1)
def privmsg(bot, ev):
    bot.send("PRIVMSG", ev.params)
    return ev

@Hook("COMMAND", scope=1)
def part(bot, ev):
    bot.send("PART", ev.params)
    return ev

@Hook("COMMAND", scope=1)
def quit(bot, ev):
    bot.send("QUIT", ev.params)
    bot.quit()
    return ev

@Hook("COMMAND", scope=1)
def startbot(bot, ev):
    try:
        args = ev.params.split() # server, nick, prefix
        bot.master.addbot(args[0],{"server": args[1], "nick": args[2], "prefix": args[3]})
        bot.ring[args[0]].conf['join'].extend(args[4:])
        bot.ring[args[0]].start()
    except IndexError:
        bot.reply(ev.dest, "startbot name server nick prefix chans...")
    return ev

@Hook("COMMAND", scope=1)
def stopbot(bot, ev):
    bot.ring[ev.params].stop()
    return ev

@Hook("COMMAND")
def topic(bot, ev):
    preface = ev.params.strip()

    if not preface:
        return ev

    if 'topicdelim' not in bot.data:
        bot.data['topicdelim'] = "  |  "
    delim = bot.data['topicdelim']

    try:
        items = bot.topics[ev.dest][-1].strip().split(delim)
    except (KeyError,IndexError):
        items = []
    print(items)

    if preface[0] == '`':
        dlen = preface.find('`', 1)
        print(dlen)
        if dlen != -1:
            delim = bot.data['topicdelim'] = ' '+preface[1:dlen]+' '
            preface = preface[dlen+1:].strip()

    if preface:
        items.insert(0, preface)

    topic = bot.data['topicdelim'].join(items)
    bot.send("TOPIC", ev.dest+" :"+topic)
    return ev

@Hook("SENDRAW")
def onraw(bot, ev):
    print("[%s]=> "%(bot.name,)+ev.line)
    return True
