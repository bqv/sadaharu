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
def raw(bot, user, to, targ, cmd, msg):
    bot.server.raw(msg)
    return (user,to,targ,cmd,msg)

@Hook("COMMAND", commands=["exec"], scope=1)
def py(bot, user, to, targ, cmd, msg):
    nick = user['nick']
    ipring = bot.data.get("interp", None)
    if not ipring:
        bot.data["interp"] = ipring = {'env': locals()}
        ipring['env'].update(globals())
        ipring['env'].update({'say': lambda x: bot.privmsg(to, x)})
        ipring['env'].update({'notice': lambda x: bot.notice(to, x)})
    ip = ipring.get(nick, None)
    if not ip:
        ipring[nick] = ip = IRCterpreter(ipring['env'], bot)
    ip.run(nick, to, msg)
    return (user,to,targ,cmd,msg)

@Hook("COMMAND", commands=["bash"], scope=1)
def shell(bot, user, to, targ, cmd, msg):
    def process():
        print("Running: "+msg)
        with subprocess.Popen(["bash","-c",msg], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as p:
            for line in iter(p.stdout.readline, b''):
                bot.privmsg(to, line.decode('utf8').rstrip())
            print("Process returned: %d"%(p.wait(),))
    threading.Thread(target=process).start()
    return (user,to,targ,cmd,msg)

@Hook("PRIVMSG")
def short(bot, user, to, targ, msg):
    nick = user['nick']
    if msg[:4] == ">>> ":
        if nick in bot.conf.get("wheel", []):
            py(bot, user, to, targ, ">>>", msg[4:])
        else:
            print("Access denied for "+nick)
    if msg[:3] == ":: ":
        if nick in bot.conf.get("wheel", []):
            raw(bot, user, to, targ, "::", msg[3:])
        else:
            print("Access denied for "+nick)
    if msg[:2] == "$ ":
        if nick in bot.conf.get("wheel", []):
            shell(bot, user, to, targ, "$", msg[2:])
        else:
            print("Access denied for "+nick)
    return (user,to,targ,msg)

@Hook("COMMAND", scope=1)
def privmsg(bot, user, to, targ, cmd, msg):
    bot.send("PRIVMSG", msg)
    return (user,to,targ,cmd,msg)

@Hook("COMMAND", scope=1)
def part(bot, user, to, targ, cmd, msg):
    bot.send("PART", msg)
    return (user,to,targ,cmd,msg)

@Hook("COMMAND", scope=1)
def quit(bot, user, to, targ, cmd, msg):
    bot.send("QUIT", msg)
    bot.server.disconnect()
    return (user,to,targ,cmd,msg)

@Hook("SENDRAW")
def onraw(bot, line):
    print("[%s]=> "%(bot.name,)+line)
    return (line,)
