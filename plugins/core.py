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

    def flushbuf(self):
        out = ''.join(self.buff).rstrip('\n').replace("\n\n", "\n \n")

        if 'File "<console>", line 1' in out:
            print(out)
            out = '\x02[;_;]\x02 '+out[out.rfind("\n")+1:]

        if len(out) > 0:
            self.bot.privmsg(self.curchan, out)
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
        ipring['env'].update({'say': lambda x: bot.privmsg(ev.dest, x)})
        ipring['env'].update({'notice': lambda x: bot.notice(ev.dest, x)})
    ip = ipring.get(ev.user.nick, None)
    if not ip:
        ipring[ev.user.nick] = ip = IRCterpreter(ipring['env'], bot)
    ip.run(ev.user.nick, ev.dest, ev.params)
    return ev

@Hook("COMMAND", commands=["bash"], scope=1)
def shell(bot, ev):
    def process():
        print("Running: "+ev.params)
        with subprocess.Popen(["bash","-c",ev.params], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as p:
            for line in iter(p.stdout.readline, b''):
                bot.privmsg(to, line.decode('utf8').rstrip())
            print("Process returned: %d"%(p.wait(),))
    threading.Thread(target=process).start()
    return ev

@Hook("PRIVMSG")
def short(bot, ev):
    if ev.msg[:4] == ">>> ":
        if ev.user.nick in bot.conf.get("wheel", []):
            ev.params = ev.msg[4:]
            ev.cmd = ">>>"
            py(bot, ev)
        else:
            print("Access denied for "+ev.user.nick)
    if ev.msg[:3] == ":: ":
        if ev.user.nick in bot.conf.get("wheel", []):
            ev.params = ev.msg[3:]
            ev.cmd = "::"
            raw(bot, ev)
        else:
            print("Access denied for "+ev.user.nick)
    if ev.msg[:2] == "$ ":
        if ev.user.nick in bot.conf.get("wheel", []):
            ev.params = ev.msg[2:]
            ev.cmd = "$"
            shell(bot, ev)
        else:
            print("Access denied for "+ev.user.nick)
    return ev

@Hook("COMMAND", scope=1)
def say(bot, ev):
    line = bytes(ev.params, "utf-8").decode("unicode_escape")
    bot.privmsg(to, line)
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

@Hook("SENDRAW")
def onraw(bot, ev):
    print("[%s]=> "%(bot.name,)+ev.line)
    return True
