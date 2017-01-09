# event.py: Classes relating to events

class HookObj:
    def __init__(self, name):
        self.name = name
        self._active = {0:[], 1:[], 2:[], 3:[]}
        self._inactive = {0:[], 1:[], 2:[], 3:[]}

    def add(self, thook, priority=1, disabled=False):
        if disabled:
            self._inactive[priority].append(thook)
        else:
            self._active[priority].append(thook)

    def remove(self, name, priority=1, disabled=False):
        if disabled:
            for i,thook in enumerate(self._inactive[priority]):
                if thook.name == name:
                    self._inactive[priority].pop(i)
        else:
            for i,thook in enumerate(self._active[priority]):
                if thook.name == name:
                    self._active[priority].pop(i)

    def _get(self, priority, with_disabled=False):
        l = self._active[priority]
        if with_disabled:
            l += self._inactive[priority]
        return l

    def active(self):
        l = []
        for hooks in list(self._active.values())[::-1]:
            l.extend(hooks)
        return l

    def inactive(self):
        l = []
        for hooks in list(self._inactive.values())[::-1]:
            l.extend(hooks)
        return l

    def all(self):
        l = []
        l.extend(self.active())
        l.extend(self.inactive())
        return l

    def low(self, with_disabled=False):
        return self._get(0, with_disabled)
    def mid(self, with_disabled=False):
        return self._get(1, with_disabled)
    def high(self, with_disabled=False):
        return self._get(2, with_disabled)
    def urgent(self, with_disabled=False):
        return self._get(3, with_disabled)

class Events:
    hooks = dict((s,HookObj(s)) for s in [
                "SEND","SENDRAW","READ","READRAW","PING","PONG","PRIVMSG",
                "NICK","NOTICE","RESPONSE","COMMAND","WELCOME","JOIN",
                "MODE","INVITE","PART","QUIT","TOPIC"])

    def __init__(self, bot):
        self.bot = bot

    def call(self, ev):
        self.runhooks(self.hooks[ev.name].urgent(), ev)
        self.runhooks(self.hooks[ev.name].high(), ev)
        self.runhooks(self.hooks[ev.name].mid(), ev)
        self.runhooks(self.hooks[ev.name].low(), ev)
        return ev

    def runhooks(self, hookset, ev):
        for hook in hookset:
            if not hook(self.bot, ev):
                raise EventCancelled(hook.name)
    
class EventCancelled(Exception):
    pass

class AbstractEvent():
    def __init__(self):
        pass
    def fire(self, bot):
        return bot.event.call(self)

class AbstractUserEvent(AbstractEvent):
    def __init__(self, user):
        AbstractEvent.__init__(self)
        self.user = user

class UserOperationEvent(AbstractUserEvent):
    def __init__(self, user, params):
        AbstractUserEvent.__init__(self, user)
        self.oper = self.name
        self.params = params#.split(':', 1)[-1]

class DirectedOperationEvent(UserOperationEvent):
    def __init__(self, user, line):
        UserOperationEvent.__init__(self, user, line)
        try:
            (self.dest, self._msg) = self.params.split(' ', 1)
        except ValueError:
            self.dest = self.params
            self._msg = ":"
        self.msg = self._msg.split(':', 1)[-1]
