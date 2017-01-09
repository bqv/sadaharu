# google.py: A google plugin

import traceback

from google import images
from google import currency
from google import calculator
from google import standard_search

from hooks import Hook

search = standard_search.search
search_images = images.search
convert_currency = currency.convert
exchange_rate = currency.exchange_rate
calculate = calculator.calculate

GOOGLE = "\x0312G\x0304o\x0307o\x0312g\x0303l\x0304e"

@Hook('COMMAND', commands=["google", "goog"])
def g(bot, ev):
    title = "\x0314\x02[\x02"+GOOGLE+"\x0314 Search\x02]\x02 - \x0F"+ev.params
    try:
        args = ev.params.split()
        params = ev.params
        index = 0
        if len(args) > 1:
            try:
                params = ' '.join(args[:-1])
                index = int(args[-1]) - 1
            except ValueError:
                params = ev.params
        page = search(params)
        results = [r for r in page if r.link != None]
        for i, result in enumerate(results):
            if i == index:
                bot.reply(ev.dest, title+" | \x02%d\x02. %s \x0314%% %s"%(i+1, result.name, result.link))
    except Exception as e:
        traceback.print_exc()
        raise e
    return ev
