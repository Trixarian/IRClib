#!/usr/bin/python
#####################################
# Trixar_za's IRClib
# By Brenton Edgar Scott
# Released under the CC0 License
#####################################
import socket, asyncore, asynchat, re

class Client(asynchat.async_chat):
	def __init__(self, nick="IRCTest", host="localhost", port=6667, password=None, ident="irc", 
				 realname="N/A", modes=None, channels=None, parser=None, reconnect=False, debug=False):
		# Each value has a default and it's completely possible to initialize the class
		# without any parameters, but all that does is create an IRC client that idles on
		# your localhost IRC Server and sends PING replies. That's not very useful now, is it?
		# Instead pass some parameters to the class like this:
		# Client("IRCer", "irc.network.com", channels="#Home,#Awesome" parser=irc_parser)
		#
		# As you can see, the first to parameters are the IRC Nickname and the IRC Server Address,
		# while the rest use their variable name to override the default. 
		# It's been intentionally written this way to make it easier to create the client connection.
		# For more control, use the list below to pass more powerful parameters to the Class:
		# nick      - String value - The nickname used by the client
		# host      - String value - The IRC server address you wish to connect to
		# port      - Number value - The IRC server port you wish to connect on
		# password  - String value - The password needed to connect to the IRC server
		# ident     - String value - The identd used by the client
		# realname  - String value - The real name used by the client
		# modes     - String value - The clients modes you wish to set after it connects
		#                            Example: modes="+xi"
		# channels  - String value - The channel(s) the client joins after it connects
		#                            Multiple channels can be joined at once by seperating
		#                            them with a comma.
		#                            Example: channels="#Home, #Start,#Help"
		# parser    - Function name - This is where you hook into the client's parser with an
		#                             external function of your own within your script. 
		#                             Check out the parse function below an example.py for
		#                             examples of how to use it.
		# reconnect - True or False - Allows the client to reconnect on Ping Timeouts or Kills. 
		# debug     - True or False - Prints debug messages to the terminal screen when set to 
		#                             True. Useful for debugging purposes.                            
		asynchat.async_chat.__init__(self)
		self.buffer = ""
		self.set_terminator("\r\n")
		self.nick = nick
		self.host = host
		self.port = port
		self.password = password
		self.ident = ident
		self.realname = realname
		self.modes = modes
		self.channels = channels
		self.parser = parser
		self.reconnect = reconnect
		self.debug = debug
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect((self.host, self.port))
		asyncore.loop()

	def write(self, text):
		# This sends data to the socket
		if self.debug: print "SENT: %s" % text
		self.push(text + "\r\n")

	def word_wrap(self, msg):
		# Splits the messages into chunks of 450 characters split by words
		# It can handle string lists and normal strings ;)
		lines = []
		line = ""
		count = 0
		try: msg = msg.split()
		except: pass
		for word in msg:
			line = line+word+" "
			count = count+1
			if (len(line)+len(word)) > 450:
				lines.append(line)
				line = ""
			elif count == len(msg) and line is not "":
				lines.append(line.strip())
		return lines

	## Some IRC command related wrappers: ##
	def raw(self, text):
		# An IRC centric alias for write
		self.write(text)

	def msg(self, target, msg):
		# Alias to send messages to an IRC channel or user
		# Works with string lists and normal string values
		for line in self.word_wrap(msg):
			self.write("PRIVMSG %s :%s" % (target, line.strip())) 

	def notice(self, target, msg):
		# Alias to send notices to an IRC channel or user
		# Works with string lists and normal string values
		for line in self.word_wrap(msg):
			self.write("NOTICE %s :%s" % (target, line.strip()))

	def act(self, target, msg):
		# Alias to send /me actions to an IRC channel or user
		# Works with string lists and normal string values
		for line in self.word_wrap(msg):
			self.write("PRIVMSG %s :\001ACTION %s\001" % (target, line.strip()))

	def mode(self, target, modes):
		# Alias to set modes on yourself or a IRC channel
		self.write("MODE %s %s" % (target, modes))

	def join(self, chan):
		# Alias to join an IRC Channel
		self.write("JOIN %s" % chan)

	def part(self, chan, msg=None):
		# Alias to part/leave an IRC Channel with an optional message
		if msg: self.write("PART %s :%s" % (chan, msg))
		else: self.write("PART %s" % chan)

	def quit(self, msg=None):
		# Alias to quit the IRC Server with an optional message
		# It also closes the socket for the client
		# This is uneffect by the auto-reconnect feature
		if msg: self.write("QUIT :%s" % msg)
		else: self.write("QUIT :Shutting down")
		self.close()

	def rclean(self, line):
		# Strips out characters that we don't want
		line = re.sub("\003([0-9][0-9]?(,[0-9][0-9]?)?)?|[^\x20-\x7E]","", line)
		return line

	def clean(self, line):
		# Strips out the : in the beginning of IRC text
		line = line.rstrip().split()
		nline = ""
		for s in line:
			if s[:1] == ":": s = s[:1].replace(":","")+s[1:]
			if nline != "": nline = nline+" "+s
			else: nline = nline+s
		line = self.rclean(nline).split()
		return line

	def getnick(self, mask):
		# Grabs the nickname out of the IRC Raw messages
		nick = mask.split("!")
		nick = nick[0]
		if nick != "":
			return nick
	
	def parse(self, line):
		# Basic IRC Parser function that can be hooked into using Client(parser=parser_function)
		# Remember that line is a list even though debug below prints it as string!
		# This is as low-level as you can get, but here's a few notes for the lazy:
		# * line[0] - The IRC server, server sent commands and user masks with PRIVMSG and NOTICE
		#             Use Client.getnick() with the user mask to grab the nickname
		# * line[1] - Numerics and IRC Commands sent by another user
		# * line[2] - With PRIVMSG or NOTICE this where the channel is located with channel messages
		#             or your nickname if it's a private conversion
		#             See example.py for how to grab the correct target
		# * line[3] - This is the first word sent by PRIVMSG or NOTICE - normally used for commands
		#             Use line[3:] to get all the text sent by PRIVMSG or NOTICE
		# * line[4:] - The rest of the PRIVMSG or NOTICE - normally used for the command args
		# Please Note: Using line[3:] and line[4:] will slice the list - you need to join it to make
		#              a proper string value.
		if self.debug: print " ".join(line)
		if line[0] == "PING": self.write("PONG %s" % line[1])
		if line[1] == "005":
			if self.modes: self.mode(self.nick, self.modes)
			# Joins the given comma seperated channels auto-magically:
			if self.channels:
				for chan in self.channels.split(","):
					self.join(chan)
		if self.parser: self.parser(self, line)

	## Now let's get the connection handling done: ##
	def handle_connect(self):
		# The Commands that are run the moment you connect to the IRC Server
		# Normally just for Authentication Purposes
		self.write("NICK %s" % self.nick)
		self.write("USER %s 0 0 :%s" % (self.ident, self.realname))
		if self.password: self.write("PASS %s" % self.password)

	def collect_incoming_data(self, data):
		self.buffer += data

	def found_terminator(self):
		# Cleans the buffer string of unwanted parts and turns it into a list
		self.parse(self.clean(self.buffer))
		self.buffer = ""

	## Code to handle auto-reconnecting: ##
	def handle_error(self):
		if self.reconnect:
			if self.debug: print "Disconnected. Restarting Connection..."
			asynchat.async_chat.__init__(self)
			self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
			self.connect((self.host, self.port))
		else: self.close()

	def handle_close(self):
		if self.reconnect:
			if self.debug: print "Disconnected. Restarting Connection..."
			asynchat.async_chat.__init__(self)
			self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
			self.connect((self.host, self.port))
		else: self.close()


class Server(asynchat.async_chat):
	def __init__(self, host="localhost", port=6667, intro=None, parser=None, reconnect=False, debug=False):
		# Works much like Client(), but with fewer options:
		# host   - String value - The IRC server address you wish to connect to
		# port   - Number value - The IRC server port you wish to connect on
		# intro  - Function name - This is where you hook into the server's intro sequence
		#                          with an external function of your own within your script. 
		# parser - Function name - This is where you hook into the server's parser with an
		#                           external function of your own within your script. 
		# reconnect - True or False - Allows the server to reconnect on SQUIT or Ping Timeout. 
		# debug  - True or False - Prints debug messages to the terminal screen when set to 
		#                         True. Useful for debugging if you can't tell by the name.    
		asynchat.async_chat.__init__(self)   
		self.buffer = ""
		self.set_terminator("\r\n")
		self.host = host
		self.port = port
		self.intro = intro
		self.parser = parser
		self.reconnect = reconnect
		self.debug = debug
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect((self.host, self.port))
		asyncore.loop()

	def write(self, text):
		if self.debug: print "SENT: %s" % text
		self.push(text + "\r\n")

	def raw(self, text):
		# An IRC centric alias for write
		self.write(text)

	def parse(self, line):
		# Basic IRC Parser function that can be hooked into using Server(parser=parser_function)
		# Remember that line is a list even though debug below prints it as string!
		# This is as low-level as you can get, but here's a few notes for the lazy:
		# * line[0] - The IRC server, server sent commands and user masks with PRIVMSG and NOTICE
		#             Use getnick() with the user mask to grab the nickname
		# * line[1] - Numerics and IRC Commands sent by another user
		# * line[2] - With PRIVMSG or NOTICE this where the channel is located with channel messages
		#             or your nickname if it's a private conversion
		# * line[3] - This is the first word sent by PRIVMSG or NOTICE - normally used for commands
		#             Use line[3:] to get all the text sent by PRIVMSG or NOTICE
		# * line[4:] - The rest of the PRIVMSG or NOTICE - normally used for the command args
		# Please Note: Using line[3:] and line[4:] will slice the list - you need to join it to make
		#              a proper string value.
		if self.debug: print " ".join(line)
		if line[0] == "PING": self.write("PONG %s" % line[1])
		if self.parser: self.parser(self, line)

	## Now let's get the connection handling done: ##
	def handle_connect(self):
		# This is where the basic IRC Server handshake sequence goes
		# Hook into it using Server(intro=intro_function)
		if self.intro: self.intro(self)
		else: print "Please provide a proper server intro sequence"
	 
	def collect_incoming_data(self, data):
		self.buffer += data

	def found_terminator(self):
		# Cleans the buffer string of unwanted parts and turns it into a list
		self.parse(Client.clean(self.buffer))
		self.buffer = ""

	## Code to handle auto-reconnecting: ##
	def handle_error(self):
		if self.reconnect:
			if self.debug: print "Disconnected. Restarting Connection..."
			asynchat.async_chat.__init__(self)
			self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
			self.connect((self.host, self.port))
		else: self.close()

	def handle_close(self):
		if self.reconnect:
			if self.debug: print "Disconnected. Restarting Connection..."
			asynchat.async_chat.__init__(self)
			self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
			self.connect((self.host, self.port))
		else: self.close()
