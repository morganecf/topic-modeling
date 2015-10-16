"""
Dumps all submissions and comments to a text file. 
Each line is a csv: <subreddit>,<submission text>,<link text>,<comments layer1>,<comments layer2>...etc.
"""

import argparse
import redditDB
import preprocessors as pre

# Allow unicode to be piped to file 
import sys
import codecs

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

# TODO : Could filter by word length also 
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
argparser.add_argument("--username", help="mongodb username")
argparser.add_argument("--password", help="mongodb password")

params = argparser.parse_args()

username = params.username
password = params.password
host = params.host
port = params.port
db = params.db

rdb = redditDB.RedditDB(username, password, host, port, db)

submissions = rdb.submission_list()
for submission in submissions:

	# Document (line) consists of subreddit name
	subreddit = rdb.submission_belongs_to(submission)
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
		text += " " + link_content
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
			text += clean_up(" ".join(layers[x])) + ","

	# Print out the line/document 
	print text


