# sed.py: A substitution plugin

import re

from hooks import Hook

@Hook("PRIVMSG")
def sed(bot, user, to, targ, msg):
    if re.match("^(\w+[:,] )?s/.+/.+(/([gi]?){2})?$", msg):
        if utils.parse.check_for_sed(self, msg):
            parsed_msg = parse(self, msg.replace("\/", "\13"), self.lastmsgof[chan.lower()][target.lower()])
            if parsed_msg == -1:
                parsed_msg = parse(self, msg.replace("\/", "\13"), self.lastmsgof[chan.lower()]["*all"])
                if parsed_msg == -1:
                    self._msg(chan, "%s: No matches found" % (nick))
                else:
                    new_msg = re.sub(parsed_msg['to_replace'], parsed_msg['replacement'], parsed_msg['oldmsg'], 0 if parsed_msg['glob'] else 1)
                    if not '\x01' in new_msg:
                        self._msg(chan, "%s" % (new_msg.replace("\13", "/")))
                    else:
                        self._msg(chan, "*%s*" % (new_msg[8:-1].replace('\13', '/').split('\x01')[1].split(' ', 1)[1]))
            else:
                new_msg = re.sub(parsed_msg['to_replace'], parsed_msg['replacement'], parsed_msg['oldmsg'], 0 if parsed_msg['glob'] else 1)
                if not '\x01' in new_msg:
                    self._msg(chan, "<%s> %s" % (target, new_msg.replace("\13", "/")))
                else:
                    self._msg(chan, "*%s %s*" % (target, new_msg.replace('\13', '/').split('\x01')[1].split(' ', 1)[1]))
    else:
        return (user,to,targ,msg)

def parse_sed(self, bot, sedmsg, oldmsgs):
    import traceback
    import re
    split_msg = sedmsg.split('/')[1:]
    glob = False
    case = False
    if len(split_msg) == 3:
        if 'g' in split_msg[2]:
            glob = True
        if 'i' in split_msg[2]:
            case = True
    try:
        regex = re.compile(split_msg[0], re.I if case else 0)
        for msg in oldmsgs:
            if regex.search(msg) is not None:
                if case:
                    return {'to_replace': "(?i)"+split_msg[0], 'replacement': lambda match: split_msg[1].replace("&", match.group(0)), 'oldmsg': msg, 'glob': glob}
                else:
                    return {'to_replace': split_msg[0], 'replacement': lambda match: split_msg[1].replace("&", match.group(0)), 'oldmsg': msg, 'glob': glob}
    except:
        traceback.print_exc()
        pass
    return -1
