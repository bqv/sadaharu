# wolfram.py: A wolframalpha plugin

import traceback
import wolframalpha

from hooks import Hook

APPID = "HQYA53-QW2WVYRKA9"
WOLFRAM = "\x0312G\x0304o\x0307o\x0312g\x0303l\x0304e"

api = wolframalpha.Client(APPID)

@Hook('COMMAND', commands=["wolfram", "wa"])
def wolframalpha(bot, ev):
    title = "\x0314\x02[\x02W|a\x0314\x02]\x02 - \x0F"+ev.params
    try:
        response = api.query(ev.params)
        try:
            result = next(response.results)
            bot.reply(ev.dest, title+" | %s \x0315%% %s"%(result.title, result.text if result.text != None else result.img))
        except StopIteration:
            for i, result in enumerate(response.pods[:3]):
                bot.reply(ev.dest, title+" | (\x02%d of %d\x02) %s \x0315%% %s"%(i+1, len(response.pods), result.title, result.text.split("\n")[0] if result.text != None else result.img))
        if ev.cmd != "wa":
            for i, result in enumerate(response.pods):
                bot.notice(ev.user.nick, title+" | \x02%d\x02. %s \x0315%% %s"%(i+1, result.title, result.text if result.text != None else result.img))
    except Exception as e:
        traceback.print_exc()
        raise e
    return ev
