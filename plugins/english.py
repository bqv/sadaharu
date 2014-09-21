# english.py: A grammar and spelling plugin

import subprocess
import threading
import traceback
import random
import math
import re

from hooks import Hook

@Hook("PRIVMSG")
def readd(bot, ev):
    def grammar():
        document = re.sub(r"\..+?[A-z]", lambda m: m.group(0).upper(), ev.msg.strip())
        document = document[0].upper()+document[1:]+('.' if document[-1] != '.' else '')
        print("G: "+document)
        with subprocess.Popen(["diction","-qbsL","en_GB"],stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as p:
            p.stdin.write(document.encode("utf-8"))
            p.stdin.close()
            for line in list(iter(p.stdout.readline, b''))[:-2]:
                bot.notice(ev.user.nick, "\x0314"+ev.user.nick+line.decode('utf8').rstrip()[1:])
            print("Process returned: %d"%(p.wait(),))
    def spelling():
        document = ev.msg
        print("S: ", end='')
        with subprocess.Popen(["aspell","-den_GB","-a"],stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as p:
            p.stdin.write(document.encode("utf-8"))
            p.stdin.close()
            resp = list([x.split() for x in list(iter(p.stdout.readline, b''))[1:-1] if x.split()[0] != b'*'])
            print(resp)
            print("Process returned: %d"%(p.wait(),))
            if resp:
                for c in resp:
                    p = c[0].decode("utf-8")
                    if p == '&':
                        document = document.replace(c[1].decode("utf-8"), "\x02"+c[4].decode("utf-8").rstrip(',')+"\x02")
                    if p == '#':
                        document = document.replace(c[1].decode("utf-8"), "\x02"+c[4].decode("utf-8").rstrip(',')+"(?)\x02")
                bot.notice(ev.user.nick, "\x0314"+ev.user.nick+": "+document)
    if bot.name == "subluminal" and ev.user.nick in [] and ev.msg[0] != '[':
        threading.Thread(target=grammar).start()
        threading.Thread(target=spelling).start()
    return ev

