# static.py: Miscellaneous functions and data

from collections import OrderedDict
import re

umodes = OrderedDict([('q','~'), ('a','&'), ('o','@'), ('h','%'), ('v','+')])

def gettarget(sender, message):
    target = msg = None
    if ',' in message:
        preamb = message.split(',')[0]
        if not ' ' in preamb:
            target = preamb
            msg = message.split(',', 1)[1].lstrip()
    if ':' in message:
        preamb = message.split(':')[0]
        if not ' ' in preamb:
            target = preamb
            msg = message.split(':', 1)[1].lstrip()
    if target:
        return target,message
    else:
        return sender,message

def iscommand(prefix, message):
    return message.lstrip().startswith(prefix)

def getcommand(prefix, message):
    l = message[len(prefix):].split(' ', 1)
    if len(l) == 2:
        return tuple(l)
    else:
        return (l[0], None)

def unpack(x):
    n = (re.sub("([+-])([A-Za-z]+)([A-Za-z])", "\g<1>\g<2>\g<1>\g<3>", x),x)
    return re.findall('..',n[0]) if n[0] == n[1] else unpack(n[0]);
