from redditDB import RedditDB
import time

username = 'mciot'
password = 'r3dd1tmorgane'

rdb = RedditDB(username, password, "blacksun.cs.mcgill.ca", 31050, "reddit_topics")

#
# data = {}
#
# f1 = open("../data/subreddit_popularity.txt", "w")
#
# for subreddit in rdb.get_subreddits():
# 	name = subreddit.get("subreddit_name")
# 	num = rdb.num_submissions(subreddit=name)
# 	data[name] = num
# 	print name, num
# 	f1.write(str(num) + '\t' + name + '\n')
#
# f1.close()
#

f2 = open("../data/subreddit_popularity_wayback.txt", "w")

num_submissions = rdb.num_wayback_submissions()

data = {}

counter = 0
num_not_belonging = 0

start = time.time()

for submission in rdb.wayback_submission_list():
	try:
		name = rdb.submission_belongs_to(submission).get("subreddit_name")
	except AttributeError:
		print submission
		num_not_belonging += 1
		continue

	try:
		data[name] += 1
	except KeyError:
		data[name] = 1

	counter += 1
	if counter % 100000 == 0:
		print "Running for:", (time.time() - start) / 60.0, "minutes"
		print "No subreddit found for", num_not_belonging, "out of", counter, "submissions\t", (num_not_belonging / float(counter)) * 100, "%"
		print "Number of subreddits:", len(data)
		print "Percent submissions remaining:", (1 - (counter / float(num_submissions))) * 100, "%"


for subreddit, num in data.iteritems():
	s = str(num) + '\t' + str(subreddit) + '\n'
	f2.write(s)

f2.close()



