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
	for i in xrange(len(fds)):
		for word in fds[i]:
			freqdict[word] = freqdict.get(word,0) + ws[i] * fds[i][word]
	return freqdict

def pick(freqdict):
	randval = random.random() * sum(freqdict.itervalues())
	for k in freqdict:
		randval -= freqdict[k]
		if randval <= 0: return k

def addInOneDirection(wordRelations, things, depth=1, maxDepth=3):
	if depth>maxDepth: return
	if things[0] not in wordRelations:
		wordRelations[things[0]] = [1, {}]
	else:
		wordRelations[things[0]][0]+=1
	if things[0] is not english.br and len(things) > 1:
		addInOneDirection(wordRelations[things[0]][1], things[1:], depth+1)

def addFromTokens(dictionary, line):
	for x in xrange(1, len(line)-1):
		if line[x] not in dictionary:
			dictionary[line[x]] = [{},{}]
		tmp = line[:x]
		tmp.reverse()
		addInOneDirection(dictionary[line[x]][0], tmp)
		addInOneDirection(dictionary[line[x]][1], line[x+1:])
	#getTopicWords(dictionary, line[1:-1])
	#print 'markov quotients after learning:'
	#print zip(line[1:-1], [markov_quotient(dictionary, word) for word in line[1:-1]])

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
		for i in xrange(len(stuff)):
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
	
#finds the most interesting words in a line
#doesn't include breaks
def getTopicWords(dictionary, words):
	topics = list((set(words) - set(english.stopwords)) - set(english.punctuation))
	if len(topics) < 1:
		topics = words
	topicquotients = dict(zip(topics, (markov_quotient(dictionary, w) for w in topics)))
	#print 'topic words and quotients:'
	#print topicquotients
	return topicquotients

#words are in proper english order, weights in order of [level1weight, level2weight, etc]
# len(words) and len(weights) should be equal
def compilePreFrequencyTable(dictionary, words, weights=None):
	#print 'prefreqtable words', words
	if not weights or len(weights) < len(words): weights = [1]*len(words)
	elif len(words) is not len(weights): weights = weights[:len(words)]
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
	elif len(words) != len(weights): weights = weights[:len(words)]
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
	if word not in dictionary:
		return '$NULL$'
	line = [word]
	weights = (1, 3, 9, 27, 81, 243)
	while True:
		if line[0] != english.br:
			line.insert(0, pick(compilePreFrequencyTable(dictionary, line[:len(weights)], weights)))
		if line[-1] != english.br:
			line.append(pick(compilePostFrequencyTable(dictionary, line[-len(weights):], weights)))
		elif line[0] == english.br:
			break
	returnstring = english.stringify(line)#' '.join(line[1:-1]).capitalize()
	if returnstring[-1] not in english.sentence_closings: returnstring += '.'
	return returnstring
	
def markov_quotient(dictionary, word):
	if word not in dictionary: return 0
	numpres = len(dictionary[word][0])
	numposts = len(dictionary[word][1])
	precontexts = sum(dictionary[word][0][thing][0] for thing in dictionary[word][0])
	postcontexts = sum(dictionary[word][1][thing][0] for thing in dictionary[word][1])
	quotient = 1.0*(precontexts+postcontexts)/(numpres+numposts)
	return quotient

class MarkovDict:
	def __init__(self):
		self.relations={}
		self.aliases = {}
		
	def learn(self, message):
		for thing in nltk.sent_tokenize(message):
			thing = thing.lower()
			addFromLine(self.relations, thing)

	def answer(self, words):
		topictable = getTopicWords(self.relations, words)
		for thing in topictable: topictable[thing] = int(topictable[thing]*10)
		topictable = dict(topictable)
		decision = pick(topictable)
		print 'forming a line with', decision, 'from the table', topictable
		return generate(self.relations, decision)

	def words(self):
		l = self.relations.keys()
		print 'words in the dictionary:'
		print l
		return 'I printed the complete list of words to the terminal, but I thought you might like to know that I have %d words in my dictionary!'%len(l)

	def known(self, word):
		if word not in self.relations: return 'word %s not in dictionary' %word
		return 'word %s has %d contexts' %(word, self.contexts(word))
		
	def contexts(self, word):
		location = self.relations[word]
		return (sum(location[0][w][0] for w in location[0]) + sum(location[1][w][0] for w in location[1])) / 2

	def fewestContexts(self, number=10):
		if number > len(self.relations): number = len(self.relations)
		word_tuples = sorted(((word, self.contexts(word)) for word in self.relations), key=(lambda x: x[1]))
		returnWords = word_tuples[:number]
		print 'Context List:', returnWords
		return 'These %d words have the fewest contexts: %s' %(number, [w[0] for w in returnWords])

