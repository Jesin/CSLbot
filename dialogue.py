#Matthew Spain, Kevin Dodd

import random
import re
import markov
import nltk
import english

#note: at the moment only classifies messages correctly if you use correct grammar

#declaring lists of stuff
#sentenceClosings formerly contained a semicolon but I have removed it
sentenceClosings = '!?.'
greetingPhrases = ['hello', 'greetings', 'ohai', 'konnichiwa', 'good day', 'hi', 'whaddup', 'what it is, what it is', 'how\'s it hangin?', '* sigh *']
acknowledgements = ['right', 'uh-huh', 'word', 'mm', 'kay', 'IKR', 'fo shizzle', 'indeed', 'yep', 'right on', 'groovy', 'I see']
ignorelist = set(('ribbot', 'SeeBorg-sprego', 'SeeBorg-nsfw', 'Ayanami-May', 'Ayanami_May'))
questionlist = ['Who', 'What', 'When', 'Where', 'How', 'Which', 'Do', 'Why', 'Whom', 'Whose', 'Why don\'t', 'How come', 'Don\'t', 'Does', 'Doesn\'t', 'Would', 'Wouldn\'t', 'Should', 'Shouldn\'t']

markovchance=1


#functions for messing around with lines/phrases
def sentencify(line):
	if line == "": return ""
	sentences = [""]
	while(line):
		sentences[-1] += line[0]#.append(line[0])
		line = line[1:]
		if sentences[-1][-1] in sentenceClosings and line and line[0] not in sentenceClosings:
			sentences.append('')
	return sentences




#functions to determine message type (dialog acts)
def isGreeting(message):
	words = sentencify(message.lower())
	for x in greetingPhrases:
		if x in words: return True
	return False

def isQuestion(message):
	return message[-1] == '?'
	

def determineMessageType(message, speaker):
	if speaker in ignorelist: return 'Markov'
	if isGreeting(message): return 'Greeting'
	if isQuestion(message): return 'Question'
	return 'Unknown'
#	raise NotImplementedError

def greeting(message, speaker, public, mdict):
	print greetingPhrases
	return random.choice(greetingPhrases)

def confusion(message, speaker, public, mdict):
	if random.random() < markovchance:
		things = nltk.sent_tokenize(message)
		words = nltk.word_tokenize(things[-1].lower())
		words = english.fixTokenizedText(words)
		print 'making a response using markov'
		reply = mdict.answer(words)
		if reply == '$NULL$': reply = random.choice(acknowledgements)		
		return reply
	return random.choice(acknowledgements)
	
def answer(message, speaker, public, mdict):
	message = message[:-1] +  '.'
	message = message.capitalize()
	for thing in questionlist:
		if message.find(thing) == 0:
			message = message[len(thing):]
	message.replace('you', 'I')
	message = message.capitalize()
	return mdict.answer(message.split(' '))

def formResponse(message, speaker, mdict, public=True):
	messageType = determineMessageType(message, speaker)
	print 'Message type for: ', message, 'is', messageType
	responseTypes = {'Greeting':greeting, 'Unknown': confusion, 'Question':confusion}
	response = responseTypes[messageType](message, speaker, public, mdict)
	return response

def main():
	print sentencify('faith I would care of this? - No, don\'t consequences the other side of the cramped cabin. - he asked Ford patiently, - said Deep Thought. They slashed sheets of it somehow unnaturally dark tiles and they met a little years Out is to be Thursday, Arlingtonians for no playing with surgery. Meanwhile, the very good with wide skidding turns. In fact sensationally beautiful. At on a small yellow fish in Eddie, who am Vroomfondel! - What\'s the robot, - There was and having, a significant without')

if __name__ == "__main__":
	main()
