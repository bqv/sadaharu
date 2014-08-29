# autojoin.py: Join channels on startup

from hooks import Hook

@Hook("WELCOME", priority=Hook.P_URGENT)
def autojoin(bot, ev):
    for chan in bot.conf['join']:
        bot.send("JOIN", chan)
    return ev
