#Matthew Spain, Kevin Dodd

import random
import string
import sys
import nltk
import english

maxlength = 5

#beginnings and endings of lines are represented by "^^^" and "$$$", respectively

#a relation dictionary is a dictonary with words keyed to an array two subarrays: prewords and postwords
#preword and postword arrays are listed as 
#a dictionary entry looks like this:
#{word: [prewords{word: frequency}, postwords{word, frequency}]}
#prewords and postwords are dictionaries of words and frequencies {word: frequency}
#order2relations is similar but does not include a list of aliases, and it keys strings of two words to the one word before or after it
#aliases is a dictionary keying aliases to their base word and base words to a list of their aliases (including themselves)
#to alias two or more words is to say "these words can be used in place of each other on a 1:1 basis"

def synthesize(fds, ws=None):
	if not ws: ws = (1,) * len(fds)
	freqdict = {}
	
	for i in range(len(fds)):
		for word in fds[i]:
			freqdict[word] = freqdict.get(word,0) + ws[i] * fds[i][word]
	
	return freqdict

def pick(freqdict):
	randval = random.random() * sum(freqdict.itervalues())
	for k in freqdict:
		randval -= freqdict[k]
		if randval <= 0: return k
		
def finalize(message):
	#message[0:1] = message[0:1].upper()
	if message[-1] not in english.sentence_closings:
		message += '.'
	return message

def addInOneDirection(wordRelations, things, depth=1, maxDepth=3):
	if depth>maxDepth: return
	if things[0] not in wordRelations:
		wordRelations[things[0]] = [1, {}]
	else:
		wordRelations[things[0]][0]+=1
	if things[0] is not english.br and len(things) > 1:
		addInOneDirection(wordRelations[things[0]][1], things[1:], depth+1)

def addFromTokens(dictionary, line):
	for x in range(1, len(line)-1):
		if line[x] not in dictionary:
			dictionary[line[x]] = [{},{}]
		tmp = line[:x]
		tmp.reverse()
		addInOneDirection(dictionary[line[x]][0], tmp)
		addInOneDirection(dictionary[line[x]][1], line[x+1:])

def addFromLine(dictionary, rawline):
	line =  [english.br] + english.fixTokenizedText(nltk.word_tokenize(rawline)) + [english.br]
	addFromTokens(dictionary, line)
	
#used to find a dictionary of the words and frequencies that come after a particular sequence in a particular dictionary
#direction 0=pre, 1=post
#words should be in reverse english order for pre
def getFreqTable(dictionary, direction, words):
	#print 'words', words
	try:
		tmp = dictionary[words[0]][direction]
		stuff = words[1:]
		for i in range(len(stuff)):
			tmp = tmp[stuff[i]][1]
		freqdict = {}
		for thing in tmp:
			freqdict[thing] = tmp[thing][0]
		return freqdict
	except KeyError:
		#print 'whoops, error'
		return {}

def weightFreqTable(table, weight):
	for thing in table:
		table[thing] = table[thing]*weight
	return table

#words are in proper english order, weights in order of [level1weight, level2weight, etc]
# len(words) and len(weights) should be equal
def compilePreFrequencyTable(dictionary, words, weights=None):
	#print 'prefreqtable words', words
	if not weights or len(weights) < len(words): weights = [1]*len(words)
	if len(words) is not len(weights): weights = weights[:len(words)]
	if len(words) == 1:
		return weightFreqTable(getFreqTable(dictionary, 0, words[:]), weights[0])
	masterlist = {} #weightFreqTable(getFreqTable(dictionary, 0, words[:]), weights[0])
	i = 0
	thing = []
	while i < len(words):
		thing.insert(0, words[i])
		#print 'thing', thing
		otherthing = weightFreqTable(getFreqTable(dictionary, 0, thing), weights[i])
		#print otherthing
		if not masterlist: masterlist = otherthing
		else: masterlist = synthesize([masterlist, otherthing])
		#print i, masterlist
		i+=1
	return masterlist

#words are in proper english order, weights in order of [level1weight, level2weight, etc]
# len(words) and len(weights) should be equal
def compilePostFrequencyTable(dictionary, words, weights=None):
	if not weights or len(weights) < len(words): weights = [1]*len(words)
	if len(words) is not len(weights): weights = weights[:len(words)]
	if len(words) == 1:
		return weightFreqTable(getFreqTable(dictionary, 1, words[:]), weights[0])
	masterlist = {} #weightFreqTable(getFreqTable(dictionary, 0, words[:]), weights[0])
	i = 1
	thing = []
	while i <= len(words):
		thing.insert(0, words[-1*i])
		otherthing = weightFreqTable(getFreqTable(dictionary, 1, thing), weights[i-1])
		#print otherthing
		if not masterlist: masterlist = otherthing
		else: masterlist = synthesize([masterlist, otherthing])
		#print i, masterlist
		i+=1
	return masterlist
	
def generate(dictionary, word):
	maxlevel = 5
	line = [word]
	level = 1
	weights = [1, 2, 3, 4, 5, 6]
	while line[0] != english.br:
		newword = pick(compilePreFrequencyTable(dictionary, line[:level], weights))
		line.insert(0, newword)
		if level < maxlevel: level +=1
		#print line
	level = 1
	while line[-1] != english.br:
		newword = pick(compilePostFrequencyTable(dictionary, line[-1*level:], weights))
#		print 'line', line
#		print 'newword', newword
		line.append(newword)
		if level < maxlevel: level +=1
	returnstring = english.stringify(line)#' '.join(line[1:-1]).capitalize()
	if returnstring[-1] not in english.sentence_closings: returnstring += '.'
	return returnstring

class MarkovDict:
	def __init__(self):
		self.relations={}
		self.aliases = {}
		
	def learn(self, message):
		for thing in nltk.sent_tokenize(message):
			thing = thing.lower()
			addFromLine(self.relations, thing)

	def answer(self, words):
		return generate(self.relations, random.choice(self.relations.keys()))
	
	
	def words(self):
		l = self.relations.keys()
		print 'words in the dictionary:'
		print l
		return 'I printed the complete list of words to the terminal, but I thought you might like to know that I have %d words in my dictionary!'%len(l)
	
	def capscheck(self):
		masterlist = {}
		for word in self.relations:
			l = word.lower()
			if l not in masterlist: masterlist[l] = [word]
			else: masterlist[l].append(word)
		for thing in masterlist.keys():
			if len(masterlist[thing]) < 2:
				del(masterlist[thing])
		#print 'masterlist to begin with:'
		#print masterlist
		fixylist = []
		for thing in masterlist:
			masterlist[thing].sort(reverse=True)
			fixylist.append(masterlist[thing])
		#print 'fixylist:'
		#print fixylist
		for thing in fixylist:
			if thing: print self.addalias(thing)
		return 'I printed some stuff but it\'s a bit too long to say on IRC.'

		
	def known(self, word):
		if word not in self.relations: return 'word %s not in dictionary' %word
		location = self.relations[word]
		contexts = 0
		for x in location[0].itervalues(): contexts += x
		for x in location[1].itervalues(): contexts += x
		return 'word %s has %d contexts' %(word, contexts)