
from hooks import Hook

@Hook("COMMAND", commands=[])
def lenny(bot, ev):
    bot.notice(ev.dest, "( ͡° ͜ʖ ͡°)")
    return ev
