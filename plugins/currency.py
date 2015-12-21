# currency.py: A currency conversion plugin

from urllib import request
import traceback
import random
import math
import json
import re

from hooks import Hook

class Currency:
    def __init__(self, isoc, pref, post, name, *args):
        (self.isoc, self.pref, self.post, self.name) = (isoc, pref, post, name)
        self.aliases = args
        g = '|'.join(self.aliases)
        u = "("+self.isoc+("|"+self.pref if self.pref else "")+"|"+self.name+"s?"+("|"+g if g else "")+")"
        a = "("+self.isoc+("|"+self.post if self.post else "")+"|"+self.name+"s?"+("|"+g if g else "")+")"
        e = " ?" if self.isoc != "CAD" else ""
        r = "("+u+" ?(?P<val1>\d([,\d]*(\.\d+)?)?))|((?P<val2>\d([,\d]*(\.\d+)?)?)"+e+a+")"
        self.re = re.compile(r, re.I)
    def __repr__(self):
        return self.isoc

currencies = [Currency("DOGE","Ð"  ,"Ð"  ,'dogecoin'),
              Currency("mBTC","mɃ" ,"mɃ" ,'millibitcoin', 'm฿'),
               Currency("BTC","Ƀ"  ,"Ƀ"  ,'bitcoin', '฿'),
               Currency("LTC","Ł"  ,"Ł"  ,'litecoin'),
               Currency("EUR","€"  ,"€"  ,'euro'),
               Currency("GBP","£"  ,"£"  ,'pound', 'quid'),
               Currency("JPY","¥"  ,"¥"  ,'yen', '円'),
               Currency("CNY",""   ,""   ,'yuan', 'RMB', '圆', '元'),
               Currency("USD","\$" ,""   ,'dollar', 'dorras'),
               Currency("CAD",""   ,"\$" ,'canadian dollar'),
               Currency("AUD",""   ,""   ,'australian dollar'),
               Currency("NZD",""   ,""   ,'new zealand dollar'),
               Currency("PHP","₱"  ,"₱"  ,'philippine peso'),
               Currency("NIO","C\$","C\$",'cordoba','córdoba'),
               Currency("ZAR",""   ,""   ,'rand'),
               Currency("SYP",""   ,""   ,'syrian pounds'),
               Currency("ISK",""   ,""   ,'icelandic krone','krone'),
               Currency("ARS",""   ,""   ,'argentine peso'),
               Currency("DKK",""   ,""   ,'danish kroner'),
               Currency("NOK",""   ,""   ,'norwegian krone'),
               Currency("VND",""   ,""   ,'vietnamese dong'),
              ]

def fetchjson(url):
    data = request.urlopen(url).read().decode("utf-8", errors="replace")
    return json.loads(data)

def getmarket():
    url = "https://blockchain.info/ticker"
    market = {"BTC": 1.0, "mBTC": 1000}
    for price in fetchjson(url).items():
        market[price[0]] = price[1]["last"]
    url = "https://coinbase.com/api/v1/currencies/exchange_rates"
    for price in [x for x in fetchjson(url).items() if x[0][:7] == "btc_to_"]:
        market[price[0][7:].upper()] = float(price[1])
    url = "https://chain.so/api/v2/get_price/DOGE/BTC"
    n = market["DOGE"] = 0
    for price in [fetchjson(url)['data']['prices'][0]]:
        market["DOGE"] += float(price['price'])
        n += 1
    market["DOGE"] = n / market["DOGE"]
    url = "https://chain.so/api/v2/get_price/LTC/BTC"
    n = market["LTC"] = 0
    for price in [fetchjson(url)['data']['prices'][0]]:
        market["LTC"] += float(price['price'])
        n += 1
    market["LTC"] = n / market["LTC"]
    return market

def convert(mkt, val, cur, sel):
    s = "¤ \x02"+cur+"\x02 - {:2,.2f} ¤ \x02".format(val,)
    for u in [str(x) for x in currencies if str(x) != cur]:
        if (cur not in ["VND","JPY","CNY"] and u in ["VND","JPY","CNY"]) and u not in sel:
            continue
        if (cur not in ["CAD","AUD","NZD"] and u in ["CAD","AUD","NZD"]) and u not in sel:
            continue
        if (cur not in ["DOGE","LTC"] and u in ["DOGE","LTC"]) and u not in sel:
            continue
        if (cur not in ["NOK","DKK","ARS","ISK","PHP","NIO","ZAR","SYP"] and u in ["NOK","DKK","ARS","ISK","PHP","NIO","ZAR","SYP"]) and u not in sel:
            continue
        v = val * mkt[u] / mkt[cur]
        if u == "BTC":
            continue
        else:
            s += u+"\x02 - {:2,.2f} ¤ \x02".format(v,)
    return "\x0314"+s

from collections import OrderedDict

@Hook("COMMAND", commands=['cur'])
def currency(bot, ev):
    if len(ev.params) > 1 and ev.params[1] != "¤":
        l = []
        for c in currencies:
            m = [[x for x in x.groupdict().values() if x][0] for x in c.re.finditer(ev.params)]
            for x in m:
                l.append((c.isoc,float(x.replace(',',''))))
        try:
            if l:
                k = getmarket()
            sel = [x.upper() for x in re.sub(r"\W+", "", ev.params.split()[-1]).split(',')]
            for i in list(OrderedDict.fromkeys(l).keys())[:3]:
                if i[1] != 0:
                    bot.notice(ev.dest, convert(k, i[1], i[0], sel))
        except Exception as e:
            traceback.print_exc()
    return ev

