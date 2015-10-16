"""
Get db stats of submissions/comments we have per-month. 
"""

from redditDB import RedditDB
from datetime import datetime 

rdb = RedditDB("mciot", "r3dd1tmorgane", "blacksun.cs.mcgill.ca", 31050, "reddit_topics")

stats = {}

num_no_created = 0
counter = 0

submissions = rdb.get_wayback_submissions()

for submission in submissions:
	counter += 1
	if counter % 100 == 0:
		print counter 

	created = submission.get(u'created')
	if created is None:
		num_no_created += 1
		continue 

	if type(created) == float:
		date = datetime.fromtimestamp(created)
	elif type(created) == datetime:
		date = created
	else:
		print "Unknown type:", type(created), created
		continue

	year = date.year
	month = date.month 

	try:
		y = stats[year]
		try:
			stats[year][month] += 1
		except KeyError:
			stats[year][month] = 1
	except KeyError:
		stats[year] = {month:1}

print stats 

