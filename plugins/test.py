# test.py: Plugin for fun stuff

from hooks import Hook

@Hook('COMMAND')
def test(bot, ev):
    bot.privmsg(ev.dest, "合格！")
    return ev
