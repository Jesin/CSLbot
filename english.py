from nltk.corpus import stopwords
import itertools
subject_pronouns = ['i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'who', 'where']

stopwords = stopwords.words('english')

#stopwords = ["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself","yourselves"]

sentence_closings = '!?.'
punctuation = '!?.,;:'
br = None

#special cases: things ending in 'd, gonna, i've (on the way back), gotta, wanna, tis, twas, 
changes = {"'ll": 'will', "'re": 'are', "'ve": 'have', 'ca': 'can', "n't": 'not', "'m": 'am', 'gim': 'give', 'lem': 'let', 'whad': 'what', 'wha': 'what', 'wo': 'will'}
dual_changes = {('gon', 'na'): ('going', 'to'), ('got', 'ta'): ('got', 'to'), ('wan', 'na'): ('want', 'to'), ('t', 'is'): ('it', 'is'), ('t', 'was'): ('it', 'was'), ('dd', 'ya'): ('do', 'you'), ('t', 'cha'): ('do', 'you')}

#takes a list of tokens made with nltk.word_tokenize and fixes contractions and things so we like it better
def fixTokenizedText(words):
	for i in xrange(len(words)):
		if words[i] in changes: words[i] = changes[words[i]]
	for i in xrange(len(words)-1):
		if tuple(words[i:i+2]) in dual_changes:
			words[i:i+2] = list(dual_changes[tuple(words[i:i+2])])
		if words[i] in subject_pronouns and words[i+1] is "'d":
			words[i+1] = 'would'
		if words[i] in subject_pronouns and words[i+1] is "'s":
			words[i+1] = 'is'
	return words

#takes a list of tokens and properly joins it as a string
def stringify(words):
	if not words or len(words) < 1:
		return words
	returnstring = words[1]
	words = words[2:-1]
	openquote = False
	for i in xrange(len(words)):
		#print 'string is now', returnstring
		if words[i] is '"':
			if openquote:
				returnstring += words[i]
			else: returnstring += ' ' + words[i]
			openquote = not openquote
		elif words[i] in punctuation or words[i][0] is "'" and len(words[i]) < 4:
			#print 'concatenating punctuation directly to previous word'
			returnstring += words[i]
		elif returnstring.endswith('"') and openquote:
			returnstring += words[i]
		else:
			returnstring += ' ' + words[i]
	#recapitalize 'I' if necessary
	returnstring = returnstring.replace(' i ', ' I ')
	returnstring = returnstring.replace(" i'", " I'")
	return returnstring.capitalize()

