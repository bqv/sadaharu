# hooks.py: Classes relating to event hooks

from event import Events

class Hook:
    P_LOW = 0
    P_MID = 1
    P_HIGH = 2
    P_URGENT = 3

    def __init__(self, hook, priority=1, disabled=False, commands=None, scope=0):
        self.name = None
        self.event = hook
        self.priority = priority
        self.disabled = disabled
        self.scope = scope
        self.commands = commands if commands != None else []

    def __call__(self, *args):
        return self.__run__(*args)

    def __run__(self, func):
        self.name = func.__name__
        self.commands.insert(0, self.name)
        if self.event == "COMMAND":
            def wrapper(bot, ev):
                import traceback, sys
                if ev.cmd.lower() in self.commands:
                    if self.scope > 0 and ev.user.nick not in bot.conf["wheel"]:
                        print("Access denied for "+ev.user.nick+" (%s)"%(self.scope,))
                        return
                    else:
                        try:
                            func(bot, ev)
                        except:
                            errtype, value, tb = sys.exc_info()
                            bot.privmsg(ev.dest, "\x02[;_;]\x02 %s: %s" %(errtype.__name__, value))
                            traceback.print_exc()
                return ev
        else:
            def wrapper(bot, ev):
                return func(bot, ev)
        self.__run__ = wrapper
        Events.hooks[self.event].add(self, self.priority, self.disabled)
        del self.priority, self.disabled
        return func

