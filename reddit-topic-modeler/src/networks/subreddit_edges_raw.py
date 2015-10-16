"""
Get user by subreddit by count - the raw data used to generate the subreddit network. 
"""

import redditDB as rdb

# Get users 
r = rdb.RedditDB("mciot", "", "blacksun.cs.mcgill.ca", 31050, "reddit_topics")
users = r.get_users()

# Get a user's posting information 
for user in users:

	username = user.get('name')

	submissions = user.get(u"submissions") or {}
	comments = user.get(u"comments") or {}

	# First correct for $ - mongodb mistake
	if "$" in submissions:
		dollar = submissions["$"]
		for k, v in dollar.iteritems():
			try:
				submissions[k] += v
			except KeyError:
				submissions[k] = v 
		del submissions["$"]
	if "$" in comments:
		dollar = comments["$"]
		for k, v in dollar.iteritems():
			try:
				comments[k] += v
			except KeyError:
				comments[k] = v 
		del comments["$"]

	# Print out information
	for subreddit, count in submissions.iteritems():
		print username, '\t', subreddit, '\t', count, '\tsubmission'

	for subreddit, count in comments.iteritems():
		print username, '\t', subreddit, '\t', count, '\tcomment'


