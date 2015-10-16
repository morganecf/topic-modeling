from redditDB import RedditDB
import praw
import time
from requests.exceptions import HTTPError

r = praw.Reddit(user_agent='testing stuff')

username = 'mciot'
password = 'r3dd1tmorgane'

rdb = RedditDB(username, password, "blacksun.cs.mcgill.ca", 31050, "reddit_topics")

num_subreddits = rdb.num_subreddits()
print num_subreddits

f_empty = open("../data/empty_subreddits.txt", "w")
f_na = open("../data/unavailable_subreddits.txt", "w")
f_err = open("../data/error_subreddits.txt", "w")

counter = 0
num_empty = 0
num_unavailable = 0
num_errors = 0

start = time.time()

for subreddit in rdb.get_subreddits():
	try:
		praw_subreddit = r.get_subreddit(subreddit.get("subreddit_name"))
		submissions = list(praw_subreddit.get_hot(limit=1))
	except HTTPError as e:
		# Most of these will signify forbidden/private/etc subreddits
		# But sometimes will get a too many requests error
		if e.errno == 429:
			num_errors += 1
			f_err.write(str(praw_subreddit) + '\n')
		else:
			num_unavailable += 1
			f_na.write(str(praw_subreddit) + '\n')
		continue

	if len(submissions) == 0:
		f_empty.write(str(praw_subreddit) + '\n')
		num_empty += 1

	counter += 1
	if counter % 100 == 0:
		print num_empty, "are empty so far"
		print num_unavailable, "are unavailable so far"
		print num_errors, "errors so far :("
		print (counter / float(num_subreddits)) * 100, "% complete"
		print (time.time() - start) / 60.0, "minutes elapsed"

print "TOTAL NUMBER OF EMPTY SUBREDDITS:", num_empty
print "TOTAL NUMBER OF UNAVAILABLE SUBREDDITS:", num_unavailable
print "TOTAL NUMBER OF ERRORS:", num_errors
f_empty.close()
f_err.close()
f_na.close()