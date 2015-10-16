"""
Dump all wayback content to different year-month directories. 
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
argparser.add_argument("--dir", help="top125 or top500", default="top125")

params = argparser.parse_args()

username = params.username
password = params.password
host = params.host
port = params.port
db = params.db
topdir = params.dir

if params.subreddits:
	subredditsf = open(params.subreddits).read().splitlines()
else:
	subredditsf = params.subreddits

rdb = redditDB.RedditDB(username, password, host, port, db)

submissions = rdb.wayback_submission_list()

count = 0

for submission in submissions:

	if count % 100000 == 0:
		print count

	count += 1

	subreddit = rdb.submission_belongs_to(submission)
	if subreddit is None:
		continue

	# If subreddit of this submission not in list, ignore
	if subredditsf and str(subreddit.get("subreddit_name")) not in subredditsf: 
		continue

	# Get date submitted 
	created = submission.get("created")
	if type(created) == float:
		date = datetime.fromtimestamp(created)
	elif type(created) == datetime:
		date = created
	else:
		print "Unknown type:", type(created), created
		continue

	# Open corresponding dump file in append mode 
	year = str(date.year)
	month = str(date.month)
	if len(month) == 1:
		month = '0'+month
	path = '../data/data_dumps/months/' + topdir + '/dump_'+year+'-'+month+'.txt'
	dumpf = open(path, 'a')

	try:
		# Document (line) consists of subreddit name
		text = subreddit.get("subreddit_name") + ","

		# and submission text
		subtext = submission.get("submission_text")
		if subtext:
			text += clean_up(subtext)
		text += ","

		# and html content
		# link_content = pre.text_from_html(submission.get("link_content"))
		# if link_content:
		# 	text += " " + link_content.replace("\n", " ")	# Remove carriage returns
		# text += ","

		# and comments, by layer 
		# comments = rdb.comment_list(submission.get("_id"))
		# layers = {}
		# for comment in comments:
		# 	layer = comment.get("layer")
		# 	ctext = comment.get("comment_text")
		# 	try:
		# 		layers[layer].append(ctext)
		# 	except:
		# 		layers[layer] = [ctext]
		# if len(layers) > 0:
		# 	for x in range(0, max(layers.keys()) + 1):
		# 		try:
		# 			text += clean_up(" ".join(layers[x])) + ","
		# 		# For example, if layers[x] is none? 
		# 		# TODO: Why would this happen?? 
		# 		except TypeError:
		# 			text += ","

		# Write the line/document 
		dumpf.write(text + '\n')
		dumpf.close()
	except OperationFailure:
		continue

