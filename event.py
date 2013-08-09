# event.py: Classes relating to events

class Events:
    class HookObj:
        def __init__(self, name, args):
            self.name = name
            self.nargs = args
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
                        self._inactive.remove(i)
            else:
                for i,thook in enumerate(self._active[priority]):
                    if thook.name == name:
                        self._active.remove(i)

        def _get(self, priority, with_disabled=False):
            l = self._active[priority]
            if with_disabled:
                l += self._inactive[priority]
            return l

        def active(self):
            l = []
            map(l.extend, self._active.values()[::-1])
            return l

        def inactive(self):
            l = []
            map(l.extend, self._inactive.values()[::-1])
            return l

        def low(self, with_disabled=False):
            return self._get(0, with_disabled)
        def mid(self, with_disabled=False):
            return self._get(1, with_disabled)
        def high(self, with_disabled=False):
            return self._get(2, with_disabled)
        def urgent(self, with_disabled=False):
            return self._get(3, with_disabled)

    hooks = {"SEND":HookObj("SEND",2),"SENDRAW":HookObj("SENDRAW",1),"READ":HookObj("READ",3),
            "READRAW":HookObj("READRAW",1),"PING":HookObj("PING",1),"PONG":HookObj("PONG",1),
            "PRIVMSG":HookObj("PRIVMSG",4),"NICK":HookObj("NICK",1),"NOTICE":HookObj("NOTICE",2),
            "RESPONSE":HookObj("RESPONSE",3),"COMMAND":HookObj("COMMAND",5),"WELCOME":HookObj("WELCOME",0),
            "JOIN":HookObj("JOIN",2),"MODE":HookObj("MODE",4),"INVITE":HookObj("INVITE",3)}

    def __init__(self, bot):
        self.bot = bot

    def call(self, evname, args=()):
        args = self.runhooks(self.hooks[evname].urgent(), evname, args)
        args = self.runhooks(self.hooks[evname].high(), evname, args)
        args = self.runhooks(self.hooks[evname].mid(), evname, args)
        args = self.runhooks(self.hooks[evname].low(), evname, args)
        return args

    def runhooks(self, hookset, evname, args):
        for hook in hookset:
            result = None
            try:
                result = hook(*args)
            except:
                self.bot.log.exception("Wrong number of %s arguments for hook %s (%s)", evname, hook.name, str(hook))
            if result != None:
                if len(result) == self.hooks[evname].nargs:
                    args = result
                else:
                    self.bot.log.error("Bad return value from hook %s (%s)", hook.name, str(hook))
            else:
                raise CancelEvent(hook.name)
        return args
    
class CancelEvent(Exception):
    pass

