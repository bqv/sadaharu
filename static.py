# static.py: Miscellaneous functions and data

from collections import OrderedDict
import re

umodes = OrderedDict([('q','~'), ('a','&'), ('o','@'), ('h','%'), ('v','+')])

def unpack(x):
    n = (re.sub("([+-])([A-Za-z]+)([A-Za-z])", "\g<1>\g<2>\g<1>\g<3>", x),x)
    return re.findall('..',n[0]) if n[0] == n[1] else unpack(n[0]);
