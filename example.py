#!/usr/bin/python
#########################
# IRC Bot Example 
# for Trixar_za's IRClib
#########################
import random
from irclib import Client as irc

base_nick = "AsyncBot"
host = "localhost"
chan = "#Zen"

# The first parameter passed to the parser is always the socket object
# The second parameter is the raw data in the form of a list
# Note: The first parameter can be used to access the variables 
#       and functions within each irclib.Client() instance
#       This makes it a good way to keep track of and control individual
#       clients
def parser(me, line):
    # Let's grab the right target from PRIVMSG or NOTICE
    try: 
	if "PRIVMSG" in line[1] or "NOTICE" in line[1]:
	    if "#" in line[2]: target = line[2]
	    else: target = me.getnick(line[0])
    except: target = ""

    # Basic command management :P 
    try: cmd = line[3]
    except: cmd = ""
    try: args = line[4:] # Just be aware that this is still a list!
    except: args = ""

    if cmd == "!new" and me.nick == base_nick:
	# Creating new clients is as simple as running the class again!
	tnum = random.randint(1, 999)
	irc("%s%d" % (base_nick, tnum), host, channels=chan, parser=parser, debug=True)
    if cmd == "!say" and me.nick == base_nick:
	me.msg(target, args) # msg and notice doesn't care if you pass a list or string to it
    if cmd == "!autoconnect":
	if args[0] == "on" and not me.reconnect:
	    me.msg(target, "Setting auto-connect to on")
	    me.reconnect = True
	if args[0] == "off" and me.reconnect:
	    me.msg(target, "Setting auto-connect to off")
	    me.reconnect = False
    if cmd == "!quit":
	me.quit()

# Initialize the script:
irc(base_nick, host, channels=chan, parser=parser, reconnect=True, debug=True)
