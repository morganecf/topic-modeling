
# TO IMPROVE: No truncating, and get main url!! 
# TODO: probably shouldn't use .keys(), because order will change if add to dict
# really need to optimize some of these functions 
# check out how many words are the same across topics 

import preprocess as P
import evaluation as E
import save 
import redditDB as db
#import dimensionality_reduction as DR

import os

"""
Parameters: for now, are hardcoded, but will usually get these from a 
user-specified configuration file. 
"""

# LIST OF TOPICS 
topics = ('gaming', 'AskReddit', 'worldnews', 'news', 'WTF', 'aww', 'technology', 'science', 'Music',
	'movies', 'books', 'EarthPorn', 'television', 'LifeProTips', 'Showerthoughts', 'food', 'Jokes',
	'firstworldanarchists', 'FoodPorn', 'HistoryPorn', 'trees', 'leagueoflegends', 'pokemon', '4chan', 
	'MakeupAddiction', 'pcmasterrace', 'gentlemanboners', 'politics', 'Bitcoin', 'Games', 'atheism', 'nba')
topics = ('gaming', 'food', 'atheism', 'politics', 'Bitcoin', 'MakeupAddiction', 'nba', 'trees', 
	'pcmasterrace', 'movies', 'firstworldanarchists', 'HistoryPorn', 'news', 'science', 'Music')
topics = ('gaming', 'food', 'atheism', 'science', 'Bitcoin')

# COMMENT LEVEL AT WHICH TO STOP
comment_level = 1

# NUMBER OF DOCUMENTS PER TOPIC
num_docs = 100

# STOPWORDS FILE TO USE (short or long)
stopwords = 'long'
	
# MAX AND MIN WORD LENGTH THRESHOLDS
max_word_length = 15
min_word_length = 3

# THRESHOLDS FOR REMOVING COMMON WORDS
removal_threshold = 2 	# Remove words that occur less than/equal to 2 times 
removal_perc = 1 		# across 100% of docs

# WEIGHTING FUNCTION 
weighting = 'tfidf'

print weighting

# # REDUCTION METHOD
# reduction = 'lsa'
# method = 'l2'		# or frobenius
# dimensions = 500

# # DISTANCE CLASSIFICATION FUNCTION 
# distance = 'cosine'

# # NUMBER OF NEIGHBORS 
# neighbors = 1

'''
Data
'''
# Get a list of RedditDocument objects
rdb = db.RedditDB("blacksun.cs.mcgill.ca", 31050, 'ejacques', 'shellcentershell', "reddit_topics")
documents = P.getData(topics, comment_level, num_docs, rdb)
print "done getting documents:", len(documents)

'''
Preprocessing
'''
# Apply some basic preprocessing functions to it. 
# Default is not to stem. 
P.preprocess(documents, max_word_length=max_word_length, min_word_length=min_word_length, stopwords=stopwords)

# Add websites to documents 
P.addWebsites(documents)

print "done preprocessing"

# Divide into training and test set 
train, test = E.partition(documents)

'''
Feature selection
'''
# Get the matrix of words 
wordmatrix = P.findAllWords(train)

print "done getting wordmatrix"
print len(wordmatrix), "distinct words"

# Remove words that occur across all topics/documents
# (Should keep number of words sort of low or else SVD will take forever)
# if len(wordmatrix) > 10000:
#	wordmatrix = P.removeCommonWords(wordmatrix, topics, documents, threshold=removal_threshold, perc=removal_perc)

# Get the weighted document word matrix
docwordmat = P.createFrequencyMatrix(train, wordmatrix, documents, weighting)
print "Document x word train matrix done:", docwordmat.shape

# Apply dimensionality reduction 
# Try without dimensionality reduction also ... svd takes a while
#reductionFn = getattr(DR, reduction)
#reduced_matrix = DR.reductionFn(weightedDWmat, dimensions, method)

'''
Evaluation
'''
# Create and weight test vectors 
test_vectors = P.createFrequencyMatrix(test, wordmatrix, documents, weighting)
print "Document x word test matrix done:", test_vectors.shape

# Classify each of the test vectors 
#results = E.classify(docwordmat, test_vectors, train, test, distance, neighbors, weight=False)

# Get accuracy 
#accuracy = E.accuracy(results)

#print accuracy

'''
Save info to file for use in MatLab.
File named according to params used.
'''

params = "T"+str(len(topics))+"D"+str(num_docs)+"C"+str(comment_level)+weighting+".csv"

Xfilename = "trainX_"+params
Yfilename = "trainY_"+params

Xtestfilename = "testX_"+params
Ytestfilename = "testY_"+params

save.toCSV(docwordmat, topics, train, Xfilename, Yfilename)
save.toCSV(test_vectors, topics, test, Xtestfilename, Ytestfilename)

print "Done saving, sending to server..."

sshbashfile = open("sendtoserver.sh", "w")
sshbashfile.write("scp ../data/files/"+Xfilename+" mciot@ubuntu.cs.mcgill.ca:~/reddit/data\n")
sshbashfile.write("scp ../data/files/"+Yfilename+" mciot@ubuntu.cs.mcgill.ca:~/reddit/data\n")
sshbashfile.write("scp ../data/files/"+Xtestfilename+" mciot@ubuntu.cs.mcgill.ca:~/reddit/data\n")
sshbashfile.write("scp ../data/files/"+Ytestfilename+" mciot@ubuntu.cs.mcgill.ca:~/reddit/data\n")

sshbashfile.close()

os.system('bash sendtoserver.sh')

