# weather.py: A weather plugin

from hooks import Hook
from bs4 import BeautifulSoup as soupify
import requests
try:
    from urllib.request import pathname2url as urlencode
except:
    from urllib import pathname2url as urlencode

@Hook('COMMAND')
def meteo(bot, ev):
    wv = list(getweather(ev.params))
    bot.notice(ev.dest, "%s: %s" %(ev.user.nick, wv[0]))
#    for w in wv:
#        __import__('sys').stdout.buffer.write((w+'\n').encode('utf-8'))

class Weather:
    def __init__(self, x):
        url = "http://weather.yahooapis.com/forecastrss?u=f&w="
        self.woeid = x['data-woeid']
        self.location = ', '.join([x['data-country'],x['data-district_county'],x['data-city'],x['data-province_state']])
        self.latlong = "[%s, %s]" %(x['data-center_lat'],x['data-center_long'])
        self.forecast = []
        soup = soupify(requests.get(url+x['data-woeid']).text, "lxml")
        print(soup)
        for z in soup.findAll():
            if z.name.startswith("yweather"):
                if z.name.endswith("location"):
                    pass
                elif z.name.endswith("units"):
                    assert z.attrs['distance'] == "mi" # mi * 1.609344 = km
                    assert z.attrs['pressure'] == "in" # ppsi * 68.9475729 = mB
                    assert z.attrs['speed'] == "mph" # mph * 1.609344 = km/h, mph * 0.44704 = m/s
                elif z.name.endswith("wind"):
                    try:
                        c_chill = "%d\xb0C" %(round(((int(z.attrs['chill']) - 32) * 5) / 9))
                        f_chill = "%s\xb0F" %(z.attrs['chill'])
                        self.chill = "%s (%s)" %(c_chill, f_chill)
                    except ValueError:
                        self.chill = None
                    try:
                        self.direction = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"][round(int(z.attrs['direction'])/22.5)%16]
                    except ValueError:
                        self.direction = None
                    try:
                        kmph_speed = "%dkm/h" %(round(int(z.attrs['speed']) * 1.609344))
                        mps_speed = "%dm/s" %(round(int(z.attrs['speed']) * 0.44704))
                        mph_speed = "%smph" %(z.attrs['speed'])
                        self.wspeed = "%s (%s,%s)" %(kmph_speed, mph_speed, mps_speed)
                    except ValueError:
                        self.wspeed = None
                elif z.name.endswith("atmosphere"):
                    try:
                        self.humidity = "%s%%"%(z.attrs['humidity'])
                    except ValueError:
                        self.humidity = None
                    try:
                        mb_pres = "%dmbar"%(int(z.attrs['pressure'])*68.9475729)
                        ppsi_pres = "%spsi"%(z.attrs['pressure'])
                        self.pres = "%s (%s)" %(mb_pres, ppsi_pres)
                    except ValueError:
                        self.pres = None
                    try:
                        self.rising = ["steady", "rising", "falling"][int(z.attrs['rising'])]
                    except ValueError:
                        self.rising = None
                    try:
                        mi_visibility = "%d miles"%(int(z.attrs['visibility'])/100)
                        km_visibility = "%dkm"%(int(z.attrs['visibility'])*0.01609344)
                        self.visib = "%s (%s)" %(km_visibility, mi_visibility)
                    except ValueError:
                        self.visib = None
                elif z.name.endswith("astronomy"):
                    if z.attrs['sunrise'] != "":
                        self.sunrise = z.attrs['sunrise']
                    else:
                        self.sunrise = None
                    if z.attrs['sunset'] != "":
                        self.sunset = z.attrs['sunset']
                    else:
                        self.sunset = None
                elif z.name.endswith("condition"):
                    try:
                        c_temp = "%d\xb0C" %(round(((int(z.attrs['temp']) - 32) * 5) / 9))
                        f_temp = "%s\xb0F" %(z.attrs['temp'])
                        self.temp = "%s (%s)" %(c_temp, f_temp)
                    except:
                        self.temp = None
                    self.condition = "%s" %(z.attrs['text'])
                elif z.name.endswith("forecast"):
                        self.forecast.append(z.attrs)

    def name(self):
        return self.location.replace(', ,', ',')

    def cond(self):
        out = self.condition
        out += ", "
        if self.chill:
            out += self.chill
        else:
            out += self.temp
        if self.direction and self.wspeed:
            out += ", "
            out += self.direction
            out += " wind at "
            out += self.wspeed
        if self.humidity:
            out += ", "
            out += self.humidity
            out += " humid"
        if self.pres:
            out += ", pressure at "
            out += self.pres
            out += " and "
            out += self.rising
        return out

    def misc(self):
        out = "centered at "
        out += self.latlong
        if self.sunrise and self.sunset:
            out += ", sunrise: "
            out += self.sunrise
            out += ", sunset: "
            out += self.sunset
        if self.visib:
            out += ", visibility of "
            out += self.visib
        return out

    def form(self):
        longw = "\x02%s\x02: %s, %s" %(self.name(), self.cond(), self.misc())
        if len(longw) > 300:
            return "\x02%s\x02: %s" %(self.name(), self.cond())
        else:
            return longw

def getweather(location):
    try:
        url = "http://woeid.rosselliot.co.nz/lookup/"
        loc = location
        qry = urlencode(loc.lower().replace(",", " "))
        req = url+qry
        rsp = requests.get(req)
        bsp = soupify(rsp.text, "lxml")
        tbl = bsp.findAll("table")[0]
        ids = [x.attrs for x in list(tbl)[1:]]

        for x in ids[0:1]:
            w = Weather(x)
            if 'condition' in w.__dict__.keys():
                yield w.form()
            else:
                print(w.__dict__)
    except Exception as e:
        yield "NoSuchPlaceError: '%s' not found (on earth)" %(loc)

