#!/usr/bin/python3
# sadaharu.py: Main file - This project is subject to the terms of MPL v2.0; see LICENSE

import sys, os, time
import re
import imp
import json
import queue
import select
import asyncio
import datetime
import traceback
import threading, queue
import logging, logging.handlers

from irc import IRCServer
from handler import Handler
from hooks import Hook
from event import Events, AbstractEvent

me = None

class Dict(dict):
    def __setitem__(self, key, value):
        if key and key[0] == ':':
            for line in traceback.format_stack():
                sys.__stdout__.write(line+"\n")
            sys.__stdout__.write("Done - %s\n"%(key,))
        dict.__setitem__(self, key, value)

    def __getattr__(self, name):
        matches = [mb for mb in self if name in mb]
        if len(matches) == 1:
            return self[matches[0]]
        elif len(matches) == 0:
            raise AttributeError("No such member %r" %(name,))
        elif len(matches) >= 2:
            raise AttributeError("Ambiguous reference %r; %r" %(name,list(matches)))

class Bot(threading.Thread):
    def __init__(self, master, name, conf):
        threading.Thread.__init__(self)
        self.starttime = time.time()
        self.master = master
        self.ring = self.master.bots
        self.name = name
        self.conf = conf
        self.data = Dict()
        self.log = logging.getLogger(self.name)
        self.log.setLevel(logging.INFO)
        self.log.addHandler(logging.handlers.RotatingFileHandler(self.name+".log", 'a', 16*1024*1024, 99))
        self.log.addHandler(logging.StreamHandler(sys.__stdout__))
        self.enabled = not self.conf.get('disabled', False)
        self.server = IRCServer(self, self.conf['server'], self.conf['port'], self.conf.get('ssl', False))
        self.event = Events(self)
        self.handler = Handler(self)
        self.sendqueue = queue.Queue()
        self.chans = Dict()
        self.users = Dict()
        self.topics = Dict()
        self.plugins = self.loadplugins()

    def run(self):
        print("Sadaharu! - @"+self.name)
        self.server.handshake()
        while self.server.isconnected:
            try:
                line = self.sendqueue.get(False)
                self.server.raw(line)
                self.sendqueue.task_done()
            except queue.Empty:
                if self.server.ready():
                    for line in self.server.recv():
                        self.handler.handle(line)
    
    def uptime(self):
        return time.time() - self.starttime

    def uptime_s(self):
        return str(datetime.timedelta(seconds=self.uptime()))

    def mode(self, targ, *modes):
        if not modes:
            return
        uplist = []
        downlist = []
        arglist = []
        nextlist = []
        if isinstance(modes[0], str):
            modes = (modes,)
        for m in modes:
            if isinstance(m, str):
                m = (m,)
            if len(arglist) > 10:
                nextlist.append(m)
                continue
            args = m[1:]
            if len(args) == 0:
                sign, cm = m[0]
                {'+':uplist, '-':downlist}[sign].append(cm)
            else:
                for arg in m[1:]:
                    if len(arglist) > 10:
                        nextlist.append([m[0], arg])
                        continue
                    sign, cm = m[0]
                    {'+':uplist, '-':downlist}[sign].append(cm)
                    arglist.append(arg)
        line = ""
        if len(uplist) > 0:
            line += "+%s" %(''.join(uplist),)
        if len(downlist) > 0:
            line += "-%s" %(''.join(downlist),)
        if len(arglist) > 0:
            line += " %s" %(' '.join(arglist),)
        print("=mode=> "+line)
        self.send("MODE", "%s %s" %(targ, line))
        self.mode(targ, *nextlist)

    def privmsg(self, targ, msg):
        for line in str(msg).split('\n'):
            self.send("PRIVMSG", "%s :%s" %(targ, line))

    def notice(self, targ, msg):
        for line in str(msg).split('\n'):
            self.send("NOTICE", "%s :%s" %(targ, line))

    def reply(self, *args):
        if self.conf.get('notice', True):
            return self.notice(*args)
        else:
            return self.privmsg(*args)

    def loadplugins(self):
        plugins = Dict([(p[:-3],__import__(p[:-3])) for p in os.listdir(self.master.pdir) if p.endswith(".py")])
        plugincount = len(plugins)
        return plugins

    def reloadplugin(self, name):
        for ho in self.event.hooks.values():
            for pr,hooks in ho._active.items():
                for hook in hooks:
                    if hook.plugin.__name__ == name:
                        ho.remove(hook.name, pr)
            for pr,hooks in ho._inactive.items():
                for hook in hooks:
                    if hook.plugin.__name__ == name:
                        ho.remove(hook.name, pr)
        self.plugins[name] = imp.reload(self.plugins[name])

    def getnick(self):
        return self.server.nick

    def send(self, cmd, params=None):
        class SendEvent(AbstractEvent):
            name = "SEND"
            def __init__(self, oper, params):
                AbstractEvent.__init__(self)
                self.oper = oper.upper()
                self.params = params
        sev = SendEvent(cmd, params).fire(self)
        self.log.debug("[%s]-> "%(self.name,)+sev.oper+(" "+sev.params if sev.params else ""))
        if params:
            self.sendqueue.put(sev.oper+" "+sev.params)
        else:
            self.sendqueue.put(sev.oper)

    def stop(self):
        self.server.disconnect()

    def restart(self):
        self.server.disconnect()
        self.log.handlers = []
        self.ring.pop(self.name)
        self.master.addbot(self.name, self.conf)
        self.ring[self.name].start()
    
    def quit(self):
        bot.master.quit()

class Sadaharu:
    def __init__(self):
        self.boottime = time.time()
        self.cdir = os.path.dirname(os.path.realpath(__file__))
        self.pdir = os.path.join(self.cdir, "plugins")
        sys.path.insert(0, self.cdir)
        sys.path.insert(0, self.pdir)
        self.loop = asyncio.get_event_loop()
        self.conf = self.loadconfig("conf.json")
        self.bots = Dict()
        self.data = Dict({'lock':threading.RLock()})
        for kv in self.conf.items():
            self.addbot(*kv)

    def __getattr__(self, name):
        return Dict.__getattr__(self.bots, name)
    
    def uptime(self):
        return time.time() - self.boottime

    def uptime_s(self):
        return str(datetime.timedelta(seconds=self.uptime()))
            
    def addbot(self, name, botconf):
        conf = Dict(list(self.loadconfig("defconf.json").values())[0])
        conf.update(botconf)
        self.bots[name] = Bot(self, name, conf)

    def loadconfig(self, filename):
        text = open(filename).read()
        stripped = re.sub("(//.*)?\n *", "", text)
        return json.loads(stripped)

    def start(self):
        for bot in self.bots.values():
            if bot.enabled:
                bot.start()
    
    def quit(self):
        for bot in self.bots.values():
            bot.stop()
        sys.exit(0)

if __name__ == "__main__":
    me = Sadaharu()
    me.start()
