"""
This module provides functions for preprocessing document data. 
"""

#import time

import errors
import weightings
import defaultdict
import numpy as np
import reddit as r
import redditDB as db
import preprocessors as pre


'''
Utility type functions. 
'''

# Retrieves documents associated with a topic
def getDocumentsByTopic(data, topic): return filter(lambda doc: doc.topic == topic, data)

# Get number of documents in collection (N). data the list of documents 
def numDocs(data): return len(data)

# Get number of distinct words in collection (M). wordmatrix the dictionary of overall 
# word frequencies 
def numDistinctWords(wordmatrix): return len(wordmatrix)

# Get the number of times a word at the index occurs in total. (ni)
def numOccurrences(index, wordmatrix):
	word = wordmatrix.keys()[index]
	return wordmatrix[word]

''' Preprocess ''' 

# data is list of documents. stemming seems weird 
# IMPORTANT: This operates directly on the document objects. Does not return anything! 
def preprocess(doc, max_word_length=None, min_word_length=None, stopwords='short', stem=False):
	stop = pre.stopwords if stopwords == 'short' else pre.stopwords_long
	# Clean 
	text = pre.clean(doc.pure_text)
	# Remove stopwords
	text = pre.filter_by_list(text, stop)
	# Remove words of certain length
	if max_word_length and min_word_length:
		text = pre.filter_by_length(text, max_length=max_word_length, min_length=min_word_length)
	else:
		text = pre.filter_by_length(text)
	# Stem 
	if stem:
		text = pre.stem(text)
	# Now replace text with processed text 
	doc.get_words(text)

''' Get the train/test data '''

# Data is a list of documents. 
def getData(topics, comment_level, num_docs, rdb, trainpath, testpath, max_word_length=None, min_word_length=None, stopwords='short', stem=False):
	#print topics
	i = open(trainpath, 'w')
	j = open(testpath, 'w')
	count = 0
	for topic in topics:
		count += 1
		print topic + ' ' + str(count)
		#start = time.clock()
		subreddit_doc = rdb.subreddit_exists(topic)
		if subreddit_doc:
			topicObject = r.RedditTopic(subreddit_doc)
		 	submission_gen = topicObject.get_submissions()
		 	start = 0
			for submission in submission_gen:
				print str(submission) + '        ' + str(count)
				start += 1
		 		docObj = r.RedditDocument(submission, topic, comment_level=comment_level)
				preprocess(docObj, max_word_length, min_word_length, stopwords, stem)
				if start%100 == 0:
					string = docObj.topic + "," + " ".join(docObj.words) + "\n" 
					j.write(string.encode("utf8"))
				else:
					string = docObj.topic + "," + " ".join(docObj.words) + "\n"
					i.write(string.encode("utf8"))
				if start == num_docs:
					break
		else:
			print topic
			raise errors.MissingError("%s subreddit does not exist in db.", topic)
		#print "\t",time.clock()-start
	#return documents
	i.close()
	j.close()


''' For words '''

# Finds all the words and their overall frequencies in the data. 
# :param data is a list of documents
# :return dictionary of {word:frequency}
def findAllWords(data):
	matrix = defaultdict(int)
	for doc in data:
		words = doc.words
		for word in words:
			matrix[word] += 1
	return matrix

# Create the document x word matrix. Entries are word occurrences in each 
# document, weighted by a particular function. Returns numpy matrix. Each 
# DOCUMENT can be identified by its ROW index, which corresponds to index in 
# data. Each WORD can be identified by its COLUMN index, which corresponds to 
# index in wordMatrix.keys() (allwords).
def createFrequencyMatrix(data, wordmatrix, docs, weightFn):
	fn = getattr(weightings, weightFn)
	N = numDocs(docs)
	M = numDistinctWords(wordmatrix)
	allwords = wordmatrix.keys()
	matrix = np.array([[0.0]*M])	

	for i, document in enumerate(data):
		docvector = []			

		# Indexes correspond to indexes of allwords
		for j,word in enumerate(allwords):
			ni = wordmatrix[word]
			freq = float(document.words.count(word))
			weighted_freq = fn(freq, col=j, row=i, ni=ni, N=N, M=M, data=data)
			docvector.append(weighted_freq)

		matrix = np.append(matrix, [docvector], 0)

	# Get rid of first row (initialized to 0s)
	return matrix[1:, 0:]

# Remove words that occur <= threshold number of times from certain percentage
# of the documents or topics  
def removeCommonWords(wordmatrix, documents, threshold=2, perc=.95):
	reduced = {}
	for word in wordmatrix.keys():
		trues = map(lambda doc: doc.words.count(word) == threshold, documents)
		if float(trues.count(True)) / float(len(documents)) < perc:
			reduced[word] = wordmatrix[word]
	return reduced

# Remove words that occur the same amount across all documents. 
def removeCommonWords2(wordmatrix, documents):
	reduced = {}
	for word in wordmatrix.keys():
		counts = map(lambda doc: doc.words.count(word), documents)
		if counts.count(counts[0]) != len(counts):
			reduced[word] = wordmatrix[word]
	return reduced

# Quick function to add document's websites to its list of words
def addWebsites(documents):
	for doc in documents:
		doc.words += doc.websites 

''' For links '''

# Find all website links in data and their frequencies of occurence. 
def findAllLinks(data):
	sites = defaultdict(int)
	for document in data:
		for link in document.websites:
			sites[link] += 1
	return sites

# Creates a topic x link frequency matrix. Topics can be indexed by ROW (corresponds 
# to topics tuple). Links can be indexed by COLUMN (corresponds to linkmatrix.keys())
def createLinkFrequencyMatrix(topics, data, linkmatrix, weightFn):
	fn = getattr(weightings, weightFn)
	alllinks = linkmatrix.keys()
	N = len(topics)
	M = len(alllinks)
	matrix = np.array([[0]*M])
	for i,topic in enumerate(topics):
		docs = getDocumentsByTopic(data, topic)
		sublinks = []
		topicvector = []
		for doc in docs:
			sublinks.extend(doc.websites)
		for j,link in enumerate(alllinks):
			ni = linkmatrix[link]
			freq = sublinks.count(link)
			weighted_freq = fn(freq, col=j, row=i, ni=ni, N=N, M=M, data=data)
			topicvector.append(weighted_freq)
		matrix = np.append(matrix, [topicvector], 0)
	return matrix[1:, 0:]


