"""
Script to gather all cross-posts (submissions posted to more than
one subreddit.) This can be done for all subreddits or for a
provided list of subreddits. 
"""

import sys
import json
import string
from redditDB import RedditDB

# Almost all xpost titles take the form (xpost <subreddit>), where <subreddit>
# may or may not have /r/, or the parentheses may have another bracket form like {} or []. 
def extract_subreddit(title):
	# Get the single word after "xpost", after removing "from"
	subreddit = title.lower().split("xpost")[1].replace("from", "")
	subreddit = subreddit.split()[0]
	# Remove r/
	subreddit = subreddit.replace("r/", "")
	# Now remove all punctuation
	subreddit = str(subreddit).translate(None, string.punctuation)
	return subreddit


rdb = RedditDB("mciot", "r3dd1tmorgane", "blacksun.cs.mcgill.ca", 31050, "reddit_topics")
topics = None

# Check to see if a list of subreddits to 
# search through was provided. If so, try
# to open it. 
if topics is None:
	print "No subreddits specified. Going through all subreddits."
else:
	try:
		topicfile = "../data/" + topics
		topics = open(topicfile).read().splitlines()
	except IOError:
		print "Cannot find specified topics file."
		sys.exit(0)

# FOR NOW: limit number of subreddits you go through
limit = 1000

# This will contain the tally of co-occurrences.
# Preserves directionality. 
crossposts = {}

for doc in rdb.get_subreddits(topics):

	limit -= 1
	if limit == 0:
		break

	topic = doc.get("subreddit_name")
	# print "========", topic, "========"

	# Get cross-posts for this subreddit
	for xpost in rdb.xposts(topic):
		# Extract the original subreddit
		title = xpost.get("submission_title")
		original = extract_subreddit(title)
		try:
			crossposts[(original, topic)] += 1
		except KeyError:
			crossposts[(original, topic)] = 1

# Do stuff for JS visualization

nodes = list(set(list(sum(crossposts.keys(), ()))))
jnodes = map(lambda n: {"name": n}, nodes)

json_obj = {"nodes": jnodes, "links": []}

for k, v in crossposts.iteritems():
	src = nodes.index(k[0])
	trg = nodes.index(k[1])
	json_obj["links"].append({"source": src, "target": trg, "weight": v})

print len(json_obj["nodes"]), "subreddits"
print len(json_obj["links"]), "connections"

json.dump(json_obj, open("../data/xpostedgelist.json", "w"))




