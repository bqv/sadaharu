# parsing.py: Miscellaneous functions for parsing

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
        return target,msg
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
