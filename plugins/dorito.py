# dorito.py: :^)

import time
import random
import threading

from hooks import Hook

def go(send):
    while True:
        time.sleep(random.randint(500, 86400)*1000)
        send(":^)")

@Hook("JOIN")
def dorito(bot, ev):
    if ev.user.nick == bot.getnick() and ev.params in ["#programming"]:
        print("Running dorito on "+ev.params)
        send = lambda m: bot.reply(ev.params, m)
        threading.Thread(target=go, args=(send,)).start()
    return ev
