"""
Store the word distribution frequencies for each subreddit in 
mongodb. Also store words, date range, and id list of all 
subreddits used in creating word distribution. 
"""

import time 
import utils
import preprocess as P
from redditDB import RedditDB

"""
Parameters: for now, are hardcoded,
but will usually get these from a 
user-specified configuration file. 
"""

rdb = RedditDB()

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

# NUMBER OF DOCUMENTS TO USE PER TOPIC
num_docs = 100

# STOPWORDS FILE TO USE (short or long)
stopwords = 'long'
	
# MAX AND MIN WORD LENGTH THRESHOLDS
max_word_length = 15
min_word_length = 3

# THRESHOLDS FOR REMOVING COMMON WORDS
removal_threshold = 2 	# Remove words that occur less than/equal to 2 times 
removal_perc = 1 		# across 100% of docs

# Will keep track of total counts 
word_frequencies = {}
# Each subreddit has associated list of documents 
documents = {}
# Each subreddit has submission- and comment-level date ranges
dates = {}

start = time.clock()
# Get documents from mongodb while preprocessing and 
# counting overall word frequencies
for topic in topics:
	st = time.clock()
	print topic 
	s = time.clock()
	docs = P.getData([topic], comment_level, num_docs)

	# Find date range for this topic (at submission level)
	subsd, subed = utils.submission_date_range(docs)
	# Find date range for this topic (at comment level)
	commsd, commed = utils.comment_date_range(docs)
	dates[topic] = {"SSD":subsd, "SED": subed, "CSD": commsd, "CED":commed}

	print "\t",len(docs), "documents:", time.clock()-s
	s = time.clock()
	P.preprocess(docs, max_word_length=max_word_length, min_word_length=min_word_length, stopwords='long', stem=False)
	print "\tdone preprocessing:", time.clock()-s
	documents[topic] = docs
	print "\tcalculating total frequencies..."
	s = time.clock()
	for doc in docs:
		# Calculate total frequencies 
		for word in doc.words:
			try:
				word_frequencies[word] += 1
			except KeyError:
				word_frequencies[word] = 1
	print "\tdone iterating through each document:", time.clock()-s
	print "\tdone calculating total frequencies. TOTAL TIME taken:", time.clock()-st


print "done counting overall frequencies for all", len(topics), "topics:", time.clock()-start
print len(word_frequencies), "distinct words total"

print "adding to words_collection"

allwords = word_frequencies.keys()	# Order shouldn't change since don't modify word_frequencies dictionary
counts = [word_frequencies[key] for key in allwords] # So that order of counts coresponds to that of allwords

sub_startdates = []
sub_enddates = []
comm_startdates = []
comm_enddates = []
for topic,ds in dates.iteritems():
	sub_startdates.append(ds["SSD"])
	sub_enddates.append(ds["SED"])
	comm_startdates.append(ds["CSD"])
	comm_enddates.append(ds["CED"])

# Overall date range at submission level 
sub_start_date = min(sub_startdates)
sub_end_date = max(sub_enddates)
# Overall date range at comment level 
comm_start_date = min(comm_startdates)
comm_end_date = max(comm_enddates)

# Now add words to be used in distribution to database 
distribution_id = rdb.add_words(allwords, counts, topics, num_docs, sub_start_date, sub_end_date, comm_start_date, comm_end_date)

print "getting vectors by topic"

counts_by_topic = {}

start = time.clock()
# Now go through all the documents and get word counts 
# creating a vector for each topic
for topic,docs in documents.iteritems():
	print topic
	# Get flattened list of all words for a topic 
	s = time.clock()
	words = []
	for doc in docs:
		words.extend(doc.words)
	print "\tdone getting word lists:", time.clock()-s
	# Find counts for each word in distribution
	s = time.clock()
	counts = [] 
	for word in allwords:
		counts.append(words.count(word))
	print len(counts), "words counted. Took:", time.clock()-s
	counts_by_topic[topic] = counts 

	# Add individual topic distributions to database 
	rdb.add_distribution(distribution_id, topic, counts, dates[topic]["SSD"], dates[topic]["SED"], dates[topic]["CSD"], dates[topic]["CED"])

print "done getting individual vectors:", time.clock()-start


