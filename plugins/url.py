# url.py: A link plugin

import re
import json
import requests
import threading
import traceback
from bs4 import BeautifulSoup as HTML
from collections import deque

from hooks import Hook

URL_REGEX = re.compile(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')


class URLobj(object):
    def __init__(self, urilist, ctx):
        self.uris = urilist
        self.context = ctx
        threading.Thread(target=self.populate).start()
        
    def populate(self):
        self.titles = map(getTitle, self.uris)

def getTitle(uri):
    try:
        headers = requests.head(uri, timeout=1, allow_redirects=True, headers={'User-agent': 'Mozilla/5.0'}).headers
        if "text/html" not in headers.get('content-type', ""):
            title = "[\x02Error\x02: Binary file]"
            return
        if float(headers.get('content-length', headers.get('content-size', 'inf'))) > 2097152:
            title = "[\x02Error\x02: Oversized file]"
            print("no content length...")
        r = requests.get(uri, timeout=1, allow_redirects=True, headers={'User-agent': 'Mozilla/5.0'})
        page = HTML(r.text)
        titletag = page.title
        title = titletag.string if titletag else "Untitled"
    except Exception as e:
        traceback.print_exc()
        title = "Title not found :- "+repr(e)
    finally:
        return title if title else "Untitled"

def shorten(uri):
    try:
        post_url = 'https://www.googleapis.com/urlshortener/v1/url'
        payload = {'longUrl': url}
        headers = {'content-type': 'application/json'}
        r = requests.post(post_url, data=json.dumps(payload), headers=headers, timeout=1)
        return r.text
    except Exception as e:
        traceback.print_exc()
        return resize(uri, 100)

def resize(s, l):
    if len(s) < l:
        return s
    else:
        return s[:l]+"..."

def getsummary(uri, num):
    api = "https://textanalysis-text-summarization.p.mashape.com/text-summarizer-url"
    head = { "X-Mashape-Key": "O9mEmBqkaRmshQeSCFbxkPEHeQh0p13bUvqjsnSU387IK8SjVX",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json" }
    params = { "sentnum": num, "url": uri }
    try:
        r = requests.post(api, headers=head, data=params)
        print(r.headers)
        print(r.text)
        return ' '.join(r.json()["sentences"]).replace("\n"," \u21b5 ")
    except Exception as e:
        traceback.print_exc()
        return "\x0305Failed to summarise :- "+repr(e)

@Hook("PRIVMSG")
def url(bot, ev):
    if ev.msg[0] == '[' or ev.user.nick == "***":
        return ev

    matches = [mgroups[0] for mgroups in URL_REGEX.findall(ev.msg)]
    if not matches:
        return ev

    uo = URLobj(matches, ev)

    urlhist = bot.data.get("urlhist", None)
    if not urlhist:
        bot.data["urlhist"] = urlhist = deque([], 4096)

    urlhist.appendleft(uo)
    return ev

@Hook("COMMAND", commands=["header"])
def title(bot, ev):
    try:
        index = int(ev.params) - 1
    except ValueError:
        index = 0

    urlhist = bot.data.get("urlhist", [])
    uo = urlhist[index]
    urlpairs = zip(uo.titles, uo.uris)
    
    def present(pair):
        title, url = pair
        return "\x0314\"%s\" - %s" %(resize(' '.join(title.replace("\n"," ").split()).strip(), 300), shorten(url))

    for resp in map(present, [p for _,p in zip(range(4),urlpairs)]):
        bot.notice(ev.dest, resp)
    return ev
    
@Hook("COMMAND", commands=["summary", "tldr"])
def summarise(bot, ev):
    args = ev.params.split()
    num = 2
    index = 0

    if len(args) >= 1:
        try:
            index = int(args[0]) - 1
            if len(args) >= 2:
                try:
                    num = int(args[1])
                except ValueError:
                    pass
        except ValueError:
            pass

    urlhist = bot.data.get("urlhist", [])
    urls = urlhist[index].uris
    
    for smry in map(lambda u: getsummary(u,num), urls):
        print("sending "+smry)
        bot.notice(ev.dest, "\x0314TL;DR - "+resize(smry, 4500))
    return ev
    
