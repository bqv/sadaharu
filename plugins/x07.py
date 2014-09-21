# x07.py: A safety plugin

from hooks import Hook

@Hook("SEND")
def x07(bot, ev):
    if ev.params and '\x07' in ev.params:
        return False
    return ev

