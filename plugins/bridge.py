# bridge.py: A bridge plugin

import threading
import traceback
import requests
import discord
import asyncio
import difflib
import smtpd
import inbox
import time
import sys
import re

from hooks import Hook

TOKEN = 'MjE1MDU5NjA4MjMyOTE5MDQw.CpSDgw.smhe9pdnleRBdPnbty6b2H7htOI'
ID_programming = "214558081399521280"
MAILGUN = "https://api.mailgun.net/v3/mg.xa0.uk/messages"
AUTH = ("api","key-365d86a4b2c3006e8ea4a46486b7766b")

COLOURGX = re.compile(r"\x1f|\x02|\x12|\x0f|\x16|\x03(?:\d{1,2}(?:,\d{1,2})?)?")

sys.stderr = sys.stdout

@Hook('PRIVMSG')
def emailbridge(bot, ev):
    if not bot.master.data.get('email', False):
        return ev
        
    if bot.master.data['lock'].acquire(False):
        mbox = bot.master.data.get('inbox', None)
        if mbox == None:
            bot.master.data['inbox'] = mbox = setupMailbox(bot)
        bot.master.data['lock'].release()

    chans = [("subluminal","programming"), ("york","cs-york")]
    for net,chan in chans:
        if bot.name == net and ev.msg[0] != '[' and ev.user.nick != '***' and ev.dest == '#'+chan:
            if ev.msg[:8] == '\x01ACTION ' and ev.msg[-1] == '\x01':
                msg = "*"+ev.user.nick+"* "+ev.msg[8:-1]
            else:
                msg = "<"+ev.user.nick+"> "+ev.msg
            email = {
                "from": "%s+%s@mg.xa0.uk" %(net, chan),
                "to": [ "tony.olagbaiye@uk.thalesgroup.com" ],
                "subject": time.strftime("%X"),
                "text": msg
            }
            resp = requests.post(MAILGUN, auth=AUTH, data=email)
            print("MAILGUN [%d] %s" %(resp.status_code, resp.text))
    return ev

def setupMailbox(bot):
    mbox = inbox.Inbox()

    @mbox.collate
    def handle(to, sender, subject, body):
        print("SMTPD", (to,sender,subject,body))
        try:
            net,chan = to[0].split('@', 1)[0].split('+', 1)
            msg = body.split("\n")[-2]
            bot.ring[net].privmsg('#'+chan, msg)
        except Exception as e:
            traceback.print_exc()

    threading.Thread(name="SMTP", target=mbox.serve, kwargs={'address':'0.0.0.0', 'port':1025}).start()

    return mbox

@Hook('PRIVMSG', priority=Hook.P_HIGH)
def chanbridge(bot, ev):
    if "chanrelays" not in bot.master.data:
        bot.master.data['chanrelays'] = [("subluminal","programming"), ("york","cs-york"), ("snoonet", "depression"), ("snoonet", "anxiety"), ("foonetic", "xkcd")]
    for net,chan in bot.master.data.chanrelays:
        if bot.name == net and ev.msg[0] != '[' and ev.user.nick != '***' and ev.dest == '#'+chan:
            if ev.msg[:8] == '\x01ACTION ' and ev.msg[-1] == '\x01':
                msg = ev.msg[8:-1]
                nick = '* '+ev.user.nick
            else:
                msg = ev.msg
                nick = '<'+ev.user.nick+'>'
            msg = COLOURGX.sub("", msg)
            try:
                bot.ring['w3'].privmsg('#-#'+chan, '%s %s' %(nick, msg))
            except KeyError:
                print("Couldn't find Freenode-side bridge")
        if bot.name == 'w3' and ev.msg[0] != '[' and ev.user.nick != '***' and ev.dest == '#-#'+chan:
            try:
                bot.ring[net].privmsg('#'+chan, ev.msg)
            except KeyError:
                print("Couldn't find bot-side bridge")
    return ev

@Hook('PRIVMSG')
def discordbridge(bot, ev):
    if bot.name == 'earl':
        client = bot.data.get('discord', None)
        if client == None:
            bot.data['discord'] = client = setupClient(bot)

        if len(ev.user.nick) > 5 and ev.user.nick[:5] == 'earl-':
            return ev

        if ev.msg[0] != '[' and ev.user.nick != '***' and ev.dest == "#programming":
            cmd = re.match(r".d(is(c(ord)?)?)? (.*)", ev.msg)
            if cmd:
                line = discord_format(client, '@Google %s' %(cmd.group(4),))
            else:
                if ev.msg[:8] == '\x01ACTION ' and ev.msg[-1] == '\x01':
                    msg = ev.msg[8:-1]
                    nick = '* '+ev.user.nick
                else:
                    msg = ev.msg
                    nick = '<'+ev.user.nick+'>'
                line = ' %s %s' %(nick, discord_format(client, msg))
            try:
                discord_send(bot.master.loop, client, ID_programming, line)
            except Exception as e:
                traceback.print_exc()
                bot.data['discord'] = setupClient(bot)
    return ev

def discord_format(client, text):
    try:
        users = {m.name.lower(): m for m in client.get_all_members()}
        users.update({m.nick.lower(): m for m in client.get_all_members() if m.nick})
    except:
        traceback.print_exc()
        return text

    def link_nick(tag):
        print("Searching for %s" %(tag.group(0),))
        name = tag.group(0)[1:].lower()
        if name in users.keys():
            print("Found", users[name])
            return users[name].mention
        else:
            return tag.group(0)

    text = re.sub(r"@\w+", link_nick, text)
    return text

def colorhash(nick):
    rcolors = [19, 20, 22, 24, 25, 26, 27, 28, 29]
    rcolors = rcolors[1:] + [rcolors[0]]
    nc = rcolors[sum(ord(i) for i in nick) % 9] - 16
    return "\x03%d@%s\x03" %(nc, nick)

def setupClient(bot):
    async def on_ready():
        print("Discord Linked")

    async def on_message(message):
        nick = message.author.display_name
        print("[Discord] <%s/%s> %s"%(message.channel.name, nick, message.content))
        if message.author.name != "IRC" and message.channel.name == "programming":
            pfx = "[%s]" %(colorhash(nick),)
            if not not message.clean_content.strip():
                bot.ring['earl'].privmsg('#programming', "\x02%s\x02 %s"%(pfx, message.clean_content.replace("\n","\u21b5")))
            for i,item in enumerate(message.attachments):
                bot.ring['earl'].privmsg('#programming', "\x02%s (%d/%d)\x02 %s"%(pfx, i+1, len(message.attachments), item['url']))

    async def on_message_edit(before, after):
        nick = after.author.display_name
        print("[Discord] <%s/%s/Edit> %r -> %r"%(after.channel.name, nick, before.content, after.content))
        if after.author.name != "IRC" and after.channel.name == "programming":
            pfx = "[%s/Edit]" %(colorhash(nick),)
            if not not after.clean_content.strip():
                if before.clean_content != after.clean_content:
                    m_before = before.clean_content.replace("\n","\u21b5")
                    m_after = after.clean_content.replace("\n","\u21b5")
                    seqm = difflib.SequenceMatcher(None, m_before, m_after)
                    diff_output = []
                    for opcode,a0,a1,b0,b1 in seqm.get_opcodes():
                        if opcode == 'equal':
                            diff_output.append(seqm.a[a0:a1])
                        elif opcode == 'insert':
                            diff_output.append("\x02\x0303+\x03\x02" + seqm.b[b0:b1] + "\x02\x0303+\x03\x02")
                        elif opcode == 'delete':
                            diff_output.append("\x02\x0304-\x03\x02" + seqm.a[a0:a1] + "\x02\x0304-\x03\x02")
                        elif opcode == 'replace':
                            diff_output.append("\x02\x0304-\x03\x02" + seqm.a[a0:a1] + "\x02\x0304-\x03\x02")
                            diff_output.append("\x02\x0303+\x03\x02" + seqm.b[b0:b1] + "\x02\x0303+\x03\x02")
                        else:
                            diff_output = "\x02ERR\x02: unexpected opcode %s while calculating diff" %(opcode,)
                            break;
                    bot.ring['earl'].privmsg('#programming', "\x02%s\x02 %s"%(pfx, ''.join(diff_output).strip()))
            for i,item in enumerate([it for it in after.attachments if it['url'] not in [em['url'] for em in before.attachments]]):
                bot.ring['earl'].privmsg('#programming', "\x02%s (%d/??)\x02 %s"%(pfx, i+1, item['url']))

    client = bot.data.get('discord', None)
    if bot.data.get('discord', None) is None:
        client = discord.Client(loop=bot.master.loop)
        client.event(on_ready)
        client.event(on_message)
        client.event(on_message_edit)

    def runClient():
        asyncio.set_event_loop(bot.master.loop)
        client.run(TOKEN)
    threading.Thread(name="Discord", target=runClient).start()
    return client

def discord_send(loop, client, chanid, msg):
    if not client.is_logged_in:
        raise Exception('Unable to connect to Discord')
    chan = client.get_channel(ID_programming)
    asyncio.ensure_future( client.send_message(chan, msg) , loop=loop)

