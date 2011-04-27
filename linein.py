import markov
import dialogue
import pickle

def learn(mdict, fname):
	filein = open(fname)
	fulltext = filein.read()
	filein.close()
	fulltext = fulltext.split('\n')[:-1]
	
	if fulltext[0] == '<list>':
		print 'reading files from ' + fname
		fulltext = fulltext[1:]
		for text in fulltext:
			learn(mdict, text)
		print 'finished reading files from ' + fname
	else:
		print 'learning ' + fname
		for line in fulltext:
			for s in dialogue.sentencify(line):
				mdict.learn(s)
		print 'learning complete'

def main():
	fname = 'sourcetexts/' + raw_input('Enter a text file to learn from (or a list of texts): ')
	filein = open(fname)
	fulltext = filein.read()
	filein.close()
	fulltext = fulltext.split('\n')[:-1]
	print 'loading dictionary...'
	try:
		pkl_file = open('dictionary.pkl', 'rb')
		mdict = pickle.load(pkl_file)
		pkl_file.close()
		print 'dictionary loaded'
	except IOError:
		mdict = markov.MarkovDict()
		print 'error loading dictionary. Using new dictionary instead.'
	
	learn(mdict, fname)
	mdict.capscheck()
	
	print 'saving dictionary...'
	output = open('dictionary.pkl', 'wb')
	pickle.dump(mdict, output, -1)
	output.close()
	print 'save complete, ending program'
	
if __name__ == "__main__":
	main()
