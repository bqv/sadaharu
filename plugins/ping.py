# ping.py: A latency checker

from hooks import Hook

@Hook('COMMAND', commands=['pong'])
def ping(bot, ev):
    if ev.cmd.lower() == "ping":
        bot.notice(ev.dest, "Pong!")
    elif ev.cmd.lower() == "pong":
        bot.notice(ev.dest, "Ping!")
    return ev
