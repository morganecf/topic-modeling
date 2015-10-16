"""
Dumps all submissions and comments to a text file. 
Each line is a csv: <subreddit>,<submission text>,<link text>,<comments layer1>,<comments layer2>...etc.
"""

import argparse
import redditDB
import preprocessors as pre
from datetime import datetime
from pymongo.errors import OperationFailure

# Allow unicode to be piped to file 
import sys
import codecs

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

# TODO : Could filter by word length also -
# TODO : remove numbers? weird unicode stuff?? 
# TODO : Looks like "" aren't getting removed...? 

# Cleans up comments by removing non-ascii
# characters (important since otherwise won't
# be found in sorted list). Also removes links, 
# punctuation, stopwords, etc. 
# This is mostly useful for reducing the 
# size of the dataset, since LDA would 
# recognize stopwords as irrelevant. 
def clean_up(text):
	text = pre.clean(text)
	text = pre.filter_by_list(text, pre.stopwords_long)
	text = pre.remove_non_ascii(text)
	return text

argparser = argparse.ArgumentParser(description="Dump text data to a file.")
argparser.add_argument("--db", help="mongo database name", default="reddit_topics")
argparser.add_argument("--host", help="mongodb host", default="blacksun.cs.mcgill.ca")
argparser.add_argument("--port", help="mongodb port", default=31050)
argparser.add_argument("--username", help="mongodb username", required=True)
argparser.add_argument("--password", help="mongodb password", required=True)
argparser.add_argument("--subreddits", help="path to optional list of subreddits", default=None)
argparser.add_argument("--date", help="year and month (xxxx-xx)", default=None)
#argparser.add_argument("--wayback", help="include data from wayback machine", default=False)

params = argparser.parse_args()

username = params.username
password = params.password
host = params.host
port = params.port
db = params.db
date = params.date 
#wayback = params.wayback

if params.subreddits:
	subredditsf = open(params.subreddits).read().splitlines()
else:
	subredditsf = params.subreddits

if date:
	year = date.split('-')[0]
	month = date.split('-')[1]

rdb = redditDB.RedditDB(username, password, host, port, db)

#### TIMING 
# import time 
# start = time.clock()
####

# Get all of the submissions or ones from specified list of subreddits
# if subredditsf is None:
# 	submissions = rdb.submission_list()
# else:
# 	submissions = []
# 	for subreddit in subredditsf:
# 		try:
# 			submissions.extend(rdb.submission_list(subreddit=subreddit))
# 			if wayback:
# 				submissions.extend(rdb.wayback_submission_list(subreddit=subreddit))
# 		except TypeError:
# 			continue

submissions = rdb.submission_list()

### TEMPORAL STUFF - can comment out ###
f3 = open('data/data_dumps/dump_2014-03.txt', 'w')
f6 = open('data/data_dumps/dump_2014-06.txt', 'w')
f9 = open('data/data_dumps/dump_2014-09.txt', 'w')
f8 = open('data/data_dumps/dump_2014-08.txt', 'w')
f11 = open('data/data_dumps/dump_2014-11.txt', 'w')

fs = {3:f3, 6:f6, 9:f9, 8:f8, 11:f11}
####################################

for submission in submissions:

	# If date was specified, check to see if in this date range. 
	# This is faster than accessing the db directly for dates. 
	#if date:
	created = submission.get("created")
	if type(created) == float:
		date = datetime.fromtimestamp(created)
	elif type(created) == datetime:
		date = created
	else:
		#print "Unknown type:", type(created), created
		continue


	### TEMPORAL STUFF - can comment out ###
	month = date.month 
	year = date.year 
	if year != 2014:
		continue
	else:
		if not (month == 3 or month == 6 or month == 9 or month == 8 or month == 11):
			continue 
	f = fs[month]
	####################################

	try:
		subreddit = rdb.submission_belongs_to(submission)
		
		# Document (line) consists of subreddit name
		#subreddit = rdb.submission_belongs_to(submission)
		if subreddit:
			text = subreddit.get("subreddit_name") + ","
		else:
			continue

		# and submission text
		subtext = submission.get("submission_text")
		if subtext:
			text += clean_up(subtext)
		text += ","

		# and html content
		link_content = pre.text_from_html(submission.get("link_content"))
		if link_content:
			text += " " + link_content.replace("\n", " ")	# Remove carriage returns
		text += ","

		# and comments, by layer 
		comments = rdb.comment_list(submission.get("_id"))
		layers = {}
		for comment in comments:
			layer = comment.get("layer")
			ctext = comment.get("comment_text")
			try:
				layers[layer].append(ctext)
			except:
				layers[layer] = [ctext]
		if len(layers) > 0:
			for x in range(0, max(layers.keys()) + 1):
				try:
					text += clean_up(" ".join(layers[x])) + ","
				# For example, if layers[x] is none? 
				# TODO: Why would this happen?? 
				except TypeError:
					text += ","

		# Print out the line/document 
		#print text

		### TEMPORAL STUFF - can comment out ###
		f.write(text + '\n')
		################################

	except OperationFailure:
		continue

### TEMPORAL STUFF - can comment out ###
for f in fs.keys():
	fh = fs[f]
	fh.close()
################################

####
# delta = time.clock() - start
# print "\n\n"
# print "num seconds:", delta 
####
