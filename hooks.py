# hooks.py: Classes relating to event hooks

from event import Events

class Hook:
    P_LOW = 0
    P_MID = 1
    P_HIGH = 2
    P_URGENT = 3

    def __init__(self, hook, priority=1, disabled=False):
        self.name = None
        self.event = hook
        self.priority = priority
        self.disabled = disabled

    def __call__(self, func):
        return self.__run__(func)

    def __run__(self, func):
        self.name = func.__name__
        self.__run__ = func
        Events.hooks[self.event].add(self, self.priority, self.disabled)
        del self.priority, self.disabled
        return func

