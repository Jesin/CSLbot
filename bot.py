#Matthew Spain, Kevin Dodd

#derived from devshed example at http://www.devshed.com/c/a/Python/IRC-on-a-Higher-Level/1/

import irclib
import ConfigParser
import random
import pickle
import sys
import string
import datetime
import threading
irclib.DEBUG = True;

class Connection:
	def __init__(self, port = 6667, network = 'irc.freenode.net'):
		self.port = port
		self.network = network
				
class IRCBot:
	def __init__(self):
		self.connection = Connection()
		self.channels = set([])#['##tokyo-3']
		self.nick = 'cslbot'
		self.name = 'tjcsl_bot'
		self.irc = irclib.IRC()
		self.addHandlers()
		self.server = self.irc.server()
		now = datetime.datetime.now()
		self.connection = "temporary"
		self.main_thread = threading.Thread(target=self.irc.process_forever)
		
		self.check_period = 2.0
		self.checked = True
		self.timer = threading.Timer(self.check_period, self.process)
		
		#self.server.join (self.channels[0])
		
	def connect(self, port = 6667, network = 'irc.freenode.net'):
		self.connection = Connection(port, network)
		print self.connection.network, self.connection.port, self.nick, self.name
		self.server.connect(self.connection.network, self.connection.port, self.nick, ircname = self.name)
	
	def joinChannel(self, channel):
		self.channels.add(channel)
		self.server.join(channel)
	
	#Handlers

	# Generic echo handler (space added)
	# This is used to output some initial information from the server
	def handleEcho (self, connection, event):
		print
		print ' '.join (event.arguments())
	
	# Handle private messages
	def handlePrivMessage (self, connection, event):
		line = event.arguments()[0]
		connection.privmsg(event.source().split('!')[0], 'Hey, I heard you say that!')
		return
		makeResponse(event.source().split('!')[0], connection, line)

	def handlePubMessage(self, connection, event):
		connection.privmsg(event.target(), 'Hey, I heard you say that!')
		return
		speaker = event.source().split('!')[0]
		makeResponse(speaker, connection, event.arguments()[0], event.target())

	# Generic echo handler (no space added)
	def handleNoSpace (self, connection, event):
		print ' '.join (event.arguments())
	
	def addHandlers(self):
		self.irc.add_global_handler('privsmg', self.handlePrivMessage) # Private message
		self.irc.add_global_handler('pubmsg', self.handlePubMessage) # Public Message
		self.irc.add_global_handler ('welcome', self.handleEcho) # Welcome message
		self.irc.add_global_handler ('yourhost', self.handleEcho) # Host message
		self.irc.add_global_handler ('created', self.handleEcho) # Server creation message
		self.irc.add_global_handler ('myinfo', self.handleEcho) # "My info" message
		self.irc.add_global_handler ('featurelist', self.handleEcho) # Server feature list
		self.irc.add_global_handler ('luserclient', self.handleEcho) # User count
		self.irc.add_global_handler ('luserop', self.handleEcho) # Operator count
		self.irc.add_global_handler ('luserchannels', self.handleEcho) # Channel count
		self.irc.add_global_handler ('luserme', self.handleEcho) # Server client count
		self.irc.add_global_handler ('n_local', self.handleEcho) # Server client count/maximum
		self.irc.add_global_handler ('n_global', self.handleEcho) # Network client count/maximum
		self.irc.add_global_handler ('luserconns', self.handleEcho) # Record client count
		self.irc.add_global_handler ('luserunknown', self.handleEcho) # Unknown connections
		self.irc.add_global_handler ('motdstart', self.handleEcho) # Message of the day (start)
		self.irc.add_global_handler ('motd', self.handleNoSpace) # Message of the day
		self.irc.add_global_handler ('edofmotd', self.handleEcho) # Message of the day (end)
		self.irc.add_global_handler ('namreply', self.handleNoSpace) # Channel name list
		self.irc.add_global_handler ('endofnames', self.handleNoSpace) # Channel name list (end)
	
	def process(self):
		
	
	def run(self):
		self.main_thread.start()
		
	def stop(self):
		self.main_thread.join()
	
	def startRuning(self):
		try:
			# Jump into an infinite loop
			self.irc.process_forever()
		except KeyboardInterrupt:
			print 'ending program'

	

##local data not in classes
#server = 'temporary';
#bot = IRCBot()
#funcdict = {}
#funchelp = {}


## Commands


##Handlers

## Generic echo handler (space added)
## This is used to output some initial information from the server
#def handleEcho (connection, event):
   #print
   #print ' '.join (event.arguments())
   
## Handle private messages
#def handlePrivMessage (connection, event):
	#line = event.arguments()[0]
	#connection.privmsg(event.source().split('!')[0], 'Hey, I heard you say that!')
	#return
	#makeResponse(event.source().split('!')[0], connection, line)

#def handlePubMessage(connection, event):
	#connection.privmsg(event.target(), 'Hey, I heard you say that!')
	#return	

#local data not in classes
#server = 'temporary';
#bot = IRCBot()
#funcdict = {}
#funchelp = {}


## Commands


##Handlers

## Generic echo handler (space added)
## This is used to output some initial information from the server
#def handleEcho (connection, event):
   #print
   #print ' '.join (event.arguments())
   
## Handle private messages
#def handlePrivMessage (connection, event):
	#line = event.arguments()[0]
	#connection.privmsg(event.source().split('!')[0], 'Hey, I heard you say that!')
	#return
	#makeResponse(event.source().split('!')[0], connection, line)

#def handlePubMessage(connection, event):
	#connection.privmsg(event.target(), 'Hey, I heard you say that!')
	#return
	#speaker = event.source().split('!')[0]
	#makeResponse(speaker, connection, event.arguments()[0], event.target())

## Generic echo handler (no space added)
#def handleNoSpace (connection, event):
   #print ' '.join (event.arguments())

## Create an IRC object
#irc = irclib.IRC()

## Register Handlers

#irc.add_global_handler('privmsg', handlePrivMessage) # Private message
#irc.add_global_handler('pubmsg', handlePubMessage) # Public Message
#irc.add_global_handler ('welcome', handleEcho) # Welcome message
#irc.add_global_handler ('yourhost', handleEcho) # Host message
#irc.add_global_handler ('created', handleEcho) # Server creation message
#irc.add_global_handler ('myinfo', handleEcho) # "My info" message
#irc.add_global_handler ('featurelist', handleEcho) # Server feature list
#irc.add_global_handler ('luserclient', handleEcho) # User count
#irc.add_global_handler ('luserop', handleEcho) # Operator count
#irc.add_global_handler ('luserchannels', handleEcho) # Channel count
#irc.add_global_handler ('luserme', handleEcho) # Server client count
#irc.add_global_handler ('n_local', handleEcho) # Server client count/maximum
#irc.add_global_handler ('n_global', handleEcho) # Network client count/maximum
#irc.add_global_handler ('luserconns', handleEcho) # Record client count
#irc.add_global_handler ('luserunknown', handleEcho) # Unknown connections
#irc.add_global_handler ('motdstart', handleEcho) # Message of the day (start)
#irc.add_global_handler ('motd', handleNoSpace) # Message of the day
#irc.add_global_handler ('edofmotd', handleEcho) # Message of the day (end)
#irc.add_global_handler ('namreply', handleNoSpace) # Channel name list
#irc.add_global_handler ('endofnames', handleNoSpace) # Channel name list (end)

## Create a server object, connect and join the channel
#server = irc.server()
#connection = Connection()
#print connection.network, connection.port, bot.nick, bot.name
#server.connect(connection.network, connection.port, bot.nick, ircname = bot.name)
#server.join (bot.channels[0])

#try:
	## Jump into an infinite loop
	#irc.process_forever()
#except KeyboardInterrupt:
	#print 'ending program'

