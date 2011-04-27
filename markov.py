#Matthew Spain, Kevin Dodd

import random
import string
import sys

sentenceClosings = '!?.'

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
	if message[-1] not in sentenceClosings:
		message += '.'
	return message
	

class MarkovDict:
	def __init__(self):
		self.relations={}
		self.order2relations={}
		self.aliases = {}
		
		
	def addcontext(self, word1, word2):
		
		if word1 in self.aliases and self.aliases[word1] is not list: word1 = self.aliases[word1]
		if word2 in self.aliases and self.aliases[word2] is not list: word2 = self.aliases[word2]
		#commaless2 = word2 if word2[:-2] == ',' else word2
		if word1 not in self.relations:
			self.relations[word1] = ({},{})
		if word2 not in self.relations:
			self.relations[word2] = ({},{})
		if word1 not in self.relations[word2][0]: self.relations[word2][0][word1] = 1
		else: self.relations[word2][0][word1]+=1
		if word2 not in self.relations[word1][1]: self.relations[word1][1][word2] = 1
		else: self.relations[word1][1][word2]+=1
		

	def learn(self, message):
		#message[0] = message[0].lower()
		words = message.split()
		words.append('$$$')
		prev = '^^^'
		for current in words:
			c = current
			if prev in self.aliases:
				prev = self.aliases[prev]
				if type(prev) is list:
					prev = prev[0]
			if current in self.aliases:
				c = self.aliases[c]
				if type(c) is list:
					c = c[0]
			self.addcontext(prev, c)
			prev = current
		
		if len(words) <3: return
		prev = '^^^'
		mid1 = words[0]
		mid2 = words[1]
		post = words[2]
		mid = mid1 + ' ' + mid2
		postindex = 2
		while post != '$$$':
			#print 'starting order 2 learning cycle'
			#print [prev, mid, post]
			if mid not in self.order2relations:
				self.order2relations[mid] = ({}, {})
			if prev not in self.order2relations[mid][0]: self.order2relations[mid][0][prev] = 0
			self.order2relations[mid][0][prev]+=1
			if post not in self.order2relations[mid][1]: self.order2relations[mid][1][post] = 0
			self.order2relations[mid][1][post]+=1
			prev = mid1
			mid1 = mid2
			mid2 = post
			postindex+=1
			post = words[postindex]
			mid = mid1 + ' ' + mid2
		if mid not in self.order2relations:
			self.order2relations[mid] = ({}, {})
		if prev not in self.order2relations[mid][0]: self.order2relations[mid][0][prev] = 0
		self.order2relations[mid][0][prev]+=1
		if post not in self.order2relations[mid][1]: self.order2relations[mid][1][post] = 0
		self.order2relations[mid][1][post]+=1
		
		#print self.order2relations
			
	def pick(self, freqdict):
		randval = random.random() * sum(freqdict.itervalues())
		for k in freqdict:
			randval -= freqdict[k]
			if randval <= 0: return k

	def answer(self, words):
		#change this array to modify order 2 prevalence: [order, order2]
		#DON'T MAKE EITHER ONE ZERO
		weights = [1, 15]
		base = None
		count = sys.maxint
		for word in words:
			if word in self.relations:
				tmp = len(self.relations[word][0]) + len(self.relations[word][1])
				if tmp and tmp < count:
					count = tmp
					base = word
		print 'making a string around the word %s' % base
		if not count: return ''
		result = [base]
		#Change limit for sentence length here
		maxlimit = 4
		limit = maxlimit
		while result[-1] != '$$$':
			
			al = result[-1]
			if al in self.aliases:
				if self.aliases[al] is not set: al = self.aliases[al]
			
			freqdict = self.relations[al][1]
			if len(result) > 1:
				chunk = result[-2] + ' ' + result[-1]
				if chunk in self.order2relations:
					freqdict = synthesize([freqdict, self.order2relations[chunk][1]], weights)
			#print 'adding word to end from following list'
			#print freqdict
			if not limit and '$$$' in freqdict.itervalues():
				result.append('$$$')
			else:
				result.append(pick(freqdict))
			limit-=1
		
		limit = maxlimit
		while result[0] != '^^^':
			
			al = result[0]
			if al in self.aliases:
				if self.aliases[al] is not set: al = self.aliases[al]
			
			freqdict = self.relations[al][0]
			if len(result) > 2:
				chunk = result[0] + ' ' + result[1]
				if chunk in self.order2relations:
					freqdict = synthesize([freqdict, self.order2relations[chunk][0]], weights)
			#print 'adding word to start from following list:'
			#print freqdict
			if not limit and '^^^' in freqdict.itervalues():
				result.insert(0, '^^^')
			else:
				result.insert(0, pick(freqdict))
			limit-=1
		result[1] = result[1].capitalize()	
		message = ' '.join(result[1:-1])
		return finalize(message)

		return ' '.join(result[1:-1])
	
	#both word1 and word2 should already be in the dictionary
	#need to finish this
	def addalias(self, words):
		if len(words) < 2:
			return 'nope, not gonna alias that'
		for word in words:
			if word not in self.relations: return 'error: one or more words not in dictionary'
		aliaslist = words[1:]
		baseword = words[0]
	
		#taking care of order 1 here
		
		predicts = []
		postdicts = []
		for thing in words:
			predicts.append(self.relations[thing][0])
			postdicts.append(self.relations[thing][1])
			del(self.relations[thing])
		#print predicts
		#print postdicts
		self.relations[baseword] = [{},{}]
		self.relations[baseword][0] = synthesize(predicts)
		self.relations[baseword][1] = synthesize(postdicts)
		if baseword not in self.aliases or type(self.aliases[baseword])==str:
			#print 'oh noez i have a string here'
			self.aliases[baseword] = {baseword}
		#print self.aliases[baseword]
		for thing in words:
			set(self.aliases[baseword]).add(thing)
			self.aliases[thing] = baseword
		return 'aliases added, list is now ' + str(self.aliases[baseword])
	
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