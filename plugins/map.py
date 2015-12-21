# map.py: An autoresponse plugin

import re
import time

from hooks import Hook

class Trigger(object):
    def __init__(self, name, regex, action, delay):
        self.name = name
        self.update(regex)
        self.action = action # lambda bot,ev,match: [Code]
        self.delay = delay

    def __repr__(self):
        return "<Trigger '%s' (r'''%s''' -> [Code])>" %(self.name, self.s)

    def update(self, regex):
        self.s = regex
        self.regex = re.compile(regex)
        return regex

    def setdelay(self, delay):
        self.delay = delay

    def run(self, bot, ev):
        match = self.regex.match(ev.msg)
        if match:
            time.sleep(self.delay)
            self.action(bot, ev, match)
            return True
        return False

class Responder(Trigger):
    def __init__(self, name, regex, resp, asnotice, delay):
        self.notice = asnotice
        self.resp = resp
        def action(bot, ev, match):
            reply = bot.notice if self.notice else bot.privmsg
            for line in re.split("[\r\n]", resp):
                reply(ev.dest, line)
        Trigger.__init__(self, name, regex, action, delay)

    def __repr__(self):
        return "<Resp '%s' (r'''%s''' -> r'''%s''')>" %(self.name, self.s, self.resp)

class TriggerList(list):
    def __repr__(self):
        lines = map(lambda t:"{} - {}".format(*t), enumerate(map(repr,self)))
        return '\n'.join(lines)

    def addResponder(self, regex, resp, name="-untitled-", asnotice=True, delay=0.2):
        self.append(Responder(name, regex, resp, asnotice, delay))

    def addTrigger(self, regex, action, name="-untitled-", delay=0.2):
        self.append(Trigger(name, regex, action, delay))

@Hook("PRIVMSG")
def misc(bot, ev):
    maps = bot.data.get("maps", None)
    if not maps:
        bot.data["maps"] = maps = TriggerList()
        maps.addResponder(r"^pony$", r"PONIES ARE FUCKING GAY.", name="!ping")
#        maps.addTrigger(r"^\s*\\o/\s*$", lambda b,e,m: b.notice(e.dest, " | ") == b.notice(e.dest, "/ \\"), name="\o/")
#        maps.addResponder(r"^\s*o/\s*$", r"\o", name="o/", asnotice=False, delay=1.8)
#        maps.addResponder(r"^\s*\\o\s*$", r"o/", name="\o", asnotice=False, delay=1.8)
        maps.addResponder(r"^\s*\\o\\\s*$", r"/o/", name="\\o\\", asnotice=False, delay=1.8)
        maps.addResponder(r"^\s*\|o\|\s*$", r"\o\ |o| /o/", name="|o|", asnotice=False, delay=1.8)
        maps.addResponder(r"^\s*/o/\s*$", "\\o\\", name="/o/", asnotice=False, delay=1.8)
        maps.addResponder(r"^\s*/o\\\s*$", "\\o/", name="/o\\", asnotice=False, delay=1.8)
    if ev.dest.lower() != "#programming":
        return ev
    for m in maps:
        m.run(bot, ev)
    return ev
