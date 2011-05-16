#Matthew Spain, Kevin Dodd

#derived from devshed example at http://www.devshed.com/c/a/Python/IRC-on-a-Higher-Level/1/

import irclib
import ConfigParser
import dialogue
import markov
import random
import pickle
import sys
import string
import datetime
import threading
irclib.DEBUG = True;

class Connection:
	def __init__(self):
		self.port = 6667
		self.network = 'irc.freenode.net'
				
class IRCBot:
	def __init__(self):
		self.connection = Connection()
		self.channels = ['##tokyo-3']
		self.nick = 'cslbot'
		self.name = 'tjcsl_bot'
		self.owners = ['mspain', 'Jesin', 'gendo', 'phonematt']
		self.password = 'password'
		self.dictionary_name = 'dictionary'
		if self.load_dictionary():
			print 'dictionary not found, making new one'
			self.mdict = markov.MarkovDict()
		self.replyrate = 1
		self.ignorelist = set(('ribbot', 'SeeBorg-sprego', 'SeeBorg-nsfw', 'Ayanami-May', 'Ayanami_May', 'pieborg'))
		self.autosave_period = 30.0
		self.saved = True
		self.timer = threading.Timer(self.autosave_period, self.autosave)
		
		now = datetime.datetime.now()

		self.log = open('log/' + now.strftime("%Y-%m-%d %H-%M") + ' '  + self.nick + ' log.txt', 'w')
	
	def log_line(self, line):
		self.log.write(line)
		self.log.flush()
	
	def load_dictionary(self):
		try:
			print 'attempting to load dictionary...'
			pkl_file = open(self.dictionary_name + '.pkl', 'rb')
			self.mdict = pickle.load(pkl_file)
			pkl_file.close()
			print 'dictionary loaded.'
			return 0
		except IOError:
			print 'error loading dictionary'
			return 1
	
	def save_dictionary(self):
		print 'saving dictionary...'
		output = open(self.dictionary_name + '.pkl', 'wb')
		pickle.dump(self.mdict, output, -1)
		output.close()
		print 'dictionary saved'
		self.saved = True
	
	def autosave(self):
		if self.saved: return
		print 'autosaving dictionary...'
		output = open(self.dictionary_name + '_auto.pkl', 'wb')
		pickle.dump(self.mdict, output, -1)
		output.close()
		print 'autosave complete'
		self.saved = True
	
	def save_for_exit(self):
		self.save_dictionary()
		print 'erasing temporary dictionary to shrink save file'
		self.mdict = None
		print 'not actually saving bot...'
		#output = open(self.nick + '.pkl', 'wb')
		#pickle.dump(self, output, -1)
		#output.close()
		print 'bot not actually saved'
		self.saved = True
		
	def shutdown(self):
		self.save_for_exit()
		self.log.close()

#local data not in classes
server = 'temporary';
bot = IRCBot()
funcdict = {}
funchelp = {}


# Commands

def savepersona(connection, source, argument):
	bot.save_for_exit()
	connection.privmsg(source, 'Bot saved.')

def ignore(connection, source, argument):
	if argument == 'noargs':
		connection.privmsg(source, 'Ignoring ' + ', '.join(bot.ignorelist))
		return
	nicks = string.split(argument)
	bot.ignorelist.update(nicks)
	connection.privmsg(source, 'Added ' + ', '.join(nicks) + ' to ignorelist')

def unignore(connection, source, argument):
	if argument == 'noargs':
		connection.privmsg(source, 'Ignoring ' + ', '.join(bot.ignorelist))
		return
	nicks = string.split(argument)
	bot.ignorelist.difference_update(nicks)
	connection.privmsg(source, 'Removed ' + ', '.join(nicks) + ' from ignorelist')

def registerOwner(connection, source, argument):
	print "identification"
	if argument.strip() == bot.password:
		bot.owners.append(source)
		msgGroup(source + " has been added as a registered owner.")
	else:
		connection.privmsg(source, "Incorrect password; permission denied")
		msgGroup(source + " requested ownership permission and was denied due to an incorrect password")
		
def alias(connection, source, argument):
	if argument == 'noargs':
		connection.privmsg(source, 'please provide at least 2 different words to alias')
		return
	words = argument.split(' ')
	if len(words) < 2:
		connection.privmsg(source, 'please provide at least 2 different words to alias')
		return
	connection.privmsg(source, bot.mdict.addalias(words))

def save(connection, source, argument):
	bot.save_dictionary()
	connection.privmsg(source, 'Dictionary saved.')
	
def exit(connection, source, argument):
	bot.shutdown()
	connection.privmsg(source, 'Good-bye!')
	print 'ending program'
	sys.exit()
	
def known(connection, source, argument):
	connection.privmsg(source, bot.mdict.known(argument))

def words(connection, source, argument):
	connection.privmsg(source, bot.mdict.words())
	
def useless(connection, source, argument):
	if argument == 'noargs' or len(argument.split()) > 1 or not int(argument):
		connection.privmsg(source, bot.mdict.fewestContexts())
	else:
		connection.privmsg(source, bot.mdict.fewestContexts(int(argument)))
	
def commandlist(connection, source, argument):
	connection.privmsg(source, 'Available commands: ' + ', '.join(funcdict))

def help(connection, source, argument):
	response = 'I don\'t know anything about that topic.  Try using \"!list\" to see a list of commands.'
	if argument is 'noargs':
		response = 'This is the help command.  Ask about a topic with \"!help <topic>\"'
	elif argument.lower() in funcdict:
		if argument.lower() in funchelp: response = argument.lower() + ': ' + funchelp[argument.lower()]
		else: response = 'Matt added this command but didn\'t bother to add any help info for it. What a jerk.'
	connection.privmsg(source, response)

#General responder

#list of commands with linked functions, and their help strings
funcdict = {'identify':registerOwner, 'alias':alias, 'exit':exit, 'save': save, 'list':commandlist, 'help':help, 'savepersona':savepersona, 'ignore':ignore, 'unignore':unignore, 'known':known, 'words':words, 'useless':useless}

funchelp = {'identify': 'adds you to the list of owners.  Use with \"!identify <password>\"', 'alias': 'alias multiple words to mean the same thing.  Use with \"!alias <baseword> <alias1> <alias2> <alias3> <etc>\"', 'exit': 'makes me save my dictionary and persona and quit.  Use with \"!exit\"', 'save': 'saves my dictionary.  Use with \"!save\"', 'list': 'prints a list of commands.  Use with \"!list\"', 'help': 'gives help on commands and topics.  Use with \"!help <topic>\"', 'grue':'The grue is a sinister, lurking presence in the dark places of the earth. Its favorite diet is adventurers, but its insatiable appetite is tempered by its fear of light. No grue has ever been seen by the light of day, and few have survived its fearsome jaws to tell the tale.', 'savepersona':'saves the current persona. Use with \"!savepersona\"', 'ignore': 'adds nicks to the ignorelist. Use with \"!ignore\" <nick1> <nick2> <nick3> <etc>', 'unignore': 'removes nicks from the ignorelist. Use with \"!unignore <nick1> <nick2> <nick3> <etc>\"', 'known':'gives the number of contexts a word has in the dictionary. Use with \"!known <word>\"', 'useless': 'gives the words in the dictionary with the fewest contexts, and the number of contexts they have each.  If an argument is provided, it will give that many words; otherwise, 10 will be given.'}

def makeResponse(speaker, connection, message, channel=None):
	#check for commands
	if speaker in bot.ignorelist: return
	print message
	target = speaker if channel is None else channel
	if message[0]=='!':
		parts = message[1:].split(None, 1)
		cmd = parts[0]
		arg = parts[1] if len(parts) > 1 else 'noargs'
		print cmd
		print arg
		print speaker
		if cmd in funcdict and speaker in bot.owners: funcdict[cmd](connection, target, arg)
		else: connection.privmsg(target, 'command ' + cmd + ' not recognized')
		return
	
	#set up autosave timer
	bot.saved = False
	#if timer: timer.cancel()
	bot.timer.cancel()
	bot.timer = threading.Timer(bot.autosave_period, bot.autosave)
	bot.timer.start()
	
	#otherwise, go ahead and learn from the line, even if you're not going to respond to it
	bot.mdict.learn(message)
	bot.log_line(speaker + ': ' + message + '\n')
	if channel and (message.lower().find(bot.nick) >= 0 or random.random() < bot.replyrate):
		response = dialogue.formResponse(message, speaker, bot.mdict, True)
		bot.log_line('me: ' + response + '\n')
		connection.privmsg(target, response)
	else:
		connection.privmsg(target, dialogue.formResponse(message, speaker, bot.mdict))


#Handlers

# Generic echo handler (space added)
# This is used to output some initial information from the server
def handleEcho (connection, event):

   print
   print ' '.join (event.arguments())

# Talk to a specific group
def msgGroup(msg, group=bot.owners):
	for dude in group:
		server.privmsg(dude, msg)

# Handle private notices
def handlePrivNotice (connection, event):

   if event.source():
      print ':: ' + event.source() + ' ->' + event.arguments()[0]
   else:
      print event.arguments()[0]


# Handle private messages
def handlePrivMessage (connection, event):
	line = event.arguments()[0]
	makeResponse(event.source().split('!')[0], connection, line)

def handlePubMessage(connection, event):
	speaker = event.source().split('!')[0]
	makeResponse(speaker, connection, event.arguments()[0], event.target())

# Handle invitations
def handleInvite (connection, event):
	channel = event.arguments()[0]
	connection.join(channel)
	bot.channels.append(channel)
	connection.privmsg(channel, 'How could you do this to me?! I thought you didn\'t want me! Why?! Why did you have to call me now, father?!')

# Generic echo handler (space added)
# This is used to output some initial information from the server
def handleEcho (connection, event):

   print
   print ' '.join (event.arguments())

# Generic echo handler (no space added)
def handleNoSpace (connection, event):

   print ' '.join (event.arguments())

# Create an IRC object
irc = irclib.IRC()

# Register Handlers

irc.add_global_handler ('privnotice', handlePrivNotice) #Private notice
irc.add_global_handler ('invite', handleInvite) # Invite
irc.add_global_handler('privmsg', handlePrivMessage) # Private message
irc.add_global_handler('pubmsg', handlePubMessage) # Public Message
irc.add_global_handler ('welcome', handleEcho) # Welcome message
irc.add_global_handler ('yourhost', handleEcho) # Host message
irc.add_global_handler ('created', handleEcho) # Server creation message
irc.add_global_handler ('myinfo', handleEcho) # "My info" message
irc.add_global_handler ('featurelist', handleEcho) # Server feature list
irc.add_global_handler ('luserclient', handleEcho) # User count
irc.add_global_handler ('luserop', handleEcho) # Operator count
irc.add_global_handler ('luserchannels', handleEcho) # Channel count
irc.add_global_handler ('luserme', handleEcho) # Server client count
irc.add_global_handler ('n_local', handleEcho) # Server client count/maximum
irc.add_global_handler ('n_global', handleEcho) # Network client count/maximum
irc.add_global_handler ('luserconns', handleEcho) # Record client count
irc.add_global_handler ('luserunknown', handleEcho) # Unknown connections
irc.add_global_handler ('motdstart', handleEcho) # Message of the day (start)
irc.add_global_handler ('motd', handleNoSpace) # Message of the day
irc.add_global_handler ('edofmotd', handleEcho) # Message of the day (end)
irc.add_global_handler ('namreply', handleNoSpace) # Channel name list
irc.add_global_handler ('endofnames', handleNoSpace) # Channel name list (end)

# Create a server object, connect and join the channel
server = irc.server()
connection = Connection()
print connection.network, connection.port, bot.nick, bot.name
server.connect (connection.network, connection.port, bot.nick, ircname = bot.name)
server.join (bot.channels[0])

msgGroup('What do you want from me?')

try:
	# Jump into an infinite loop
	irc.process_forever()
except KeyboardInterrupt:
	bot.shutdown()
	print 'ending program'
