# hooks.py: Classes relating to event hooks

from event import Events

class Hook:
    P_LOW = 0
    P_MID = 1
    P_HIGH = 2
    P_URGENT = 3
    bot = None

    def __init__(self, hook, priority=1, disabled=False, command=None, commands=[]):
        self.name = None
        self.event = hook
        self.priority = priority
        self.disabled = disabled
        self.commands = commands
        if command:
            self.commands.append(command)

    def __call__(self, *args):
        return self.__run__(*args)

    def __run__(self, func):
        self.name = func.__name__
        if self.commands and self.event == "COMMAND":
            def wrapper(usr, to, targ, cmd, msg):
                if cmd.lower() in self.commands:
                    func(usr, to, targ, cmd, msg)
                return (usr, to, targ, cmd, msg)
        else:
            def wrapper(*args):
                return func(*args)
        self.__run__ = wrapper
        Events.hooks[self.event].add(self, self.priority, self.disabled)
        del self.priority, self.disabled
        return func

