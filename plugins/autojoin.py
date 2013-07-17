# autojoin.py: Join channels on startup

from hooks import Hook

@Hook("WELCOME", priority=Hook.P_URGENT)
def autojoin(bot):
    for chan in bot.conf['join']:
        bot.server.send("JOIN", chan)
    return ()
