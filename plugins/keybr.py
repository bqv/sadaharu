# keybr.py: A keyboard layout coverter

from hooks import Hook

qwerty  = "1234567890-=qwertyuiop[]asdfghjkl;'#\zxcvbnm,./" + '!"£$%^&*()_+QWERTYUIOP{}ASDFGHJKL:@~|ZXCVBNM<>?'
dvorak  = "1234567890[]',.pyfgcrl/=aoeuidhtns-#\;qjkxbmwvz" + '!"£$%^&*(){}@<>PYFGCRL?+AOEUIDHTNS_~|:QJKXBMWVZ'
colemak = "1234567890-=qwfpgjluy;[]arstdhneio'#\zxcvbkm,./" + '!"£$%^&*()_+QWFPGJLUY:{}ARSTDHNEIO@~|ZXCVBKM<>?'

@Hook('COMMAND', commands=[])
def d2q(bot, ev):
    bot.notice(ev.dest, "D2Q: %s"%(ev.params.translate(str.maketrans(dvorak, qwerty)),))
    return ev
@Hook('COMMAND', commands=[])
def q2d(bot, ev):
    bot.notice(ev.dest, "Q2D: %s"%(ev.params.translate(str.maketrans(qwerty, dvorak)),))
    return ev
@Hook('COMMAND', commands=[])
def c2q(bot, ev):
    bot.notice(ev.dest, "C2Q: %s"%(ev.params.translate(str.maketrans(colemak, qwerty)),))
    return ev
@Hook('COMMAND', commands=[])
def q2c(bot, ev):
    bot.notice(ev.dest, "Q2C: %s"%(ev.params.translate(str.maketrans(qwerty, colemak)),))
    return ev
@Hook('COMMAND', commands=[])
def c2d(bot, ev):
    bot.notice(ev.dest, "C2D: %s"%(ev.params.translate(str.maketrans(colemak, dvorak)),))
    return ev
@Hook('COMMAND', commands=[])
def d2c(bot, ev):
    bot.notice(ev.dest, "D2C: %s"%(ev.params.translate(str.maketrans(dvorak, colemak)),))
    return ev
