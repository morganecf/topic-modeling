'''
'''

import time
import praw
from redditDB import RedditDB

# Connect
username = 'mciot'
password = 'r3dd1tmorgane'
rdb = RedditDB(username, password, "blacksun.cs.mcgill.ca", 31050, "reddit_topics")

reddit = praw.Reddit(user_agent="my super fun project")

num_submissions = rdb.num_wayback_submissions()
counter = 0
log_interval = 10000

start = time.time()

f = open("../data/wayback_submission_praw_ids.txt", "w")

# Collect submissions
for submission in rdb.wayback_submission_list():
	# Get submission's praw_id
	praw_id = submission.get("reddit_id")

	if praw_id is None:
		continue

	f.write(praw_id + '\n')

	if counter % log_interval == 0:
		print "Progress:", counter, "praw_ids printed out of", num_submissions, (counter / float(num_submissions)) * 100, "%"
		print "Time spent:", (time.time() - start) / 60.0, "minutes"

	counter += 1

f.close()