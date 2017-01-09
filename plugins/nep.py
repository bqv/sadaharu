import re

from hooks import Hook

NEP_RE = re.compile(r'((?:[Nn][Ee][Pp])+)')
NOOT_RE = re.compile(r'((?:[Nn][Oo][Oo]+[Tt])+)')

@Hook("PRIVMSG")
@Hook("NOTICE")
def nep(bot, ev):
    if ev.dest not in ["#cs-york-off-topic", "#"] or ev.user.nick == "***":
        return ev

    neps = sum(len(x)//3 for x in NEP_RE.findall(ev.msg))
    noots = sum(len(x)//4 for x in NOOT_RE.findall(ev.msg))

    counts = bot.data.get("counts", {"neps":0, "noots":0})
    bot.data["counts"] = {"neps":counts["neps"]+neps, "noots":counts["noots"]+noots}

    return ev

@Hook("COMMAND", commands=["neps","noots"])
def counts(bot, ev):
    counts = bot.data.get("counts", {"neps":0, "noots":0})
    bot.notice(ev.dest, "%d, %d"%(counts["neps"], counts["noots"]))
    return ev

@Hook("JOIN")
def trix(bot, ev):
    if ("#programming" in ev.params) and ev.user.nick == "Trixis":
        pass#bot.privmsg("#programming", "Trixis: you should fix bouncer")
    if ("#cs-york-off-topic" in ev.params) and ev.user.nick == "nitia":
        bot.send("PART", "#cs-york-off-topic :part")
    return ev
