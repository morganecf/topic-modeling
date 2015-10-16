""" 
Script to get information about all errors in logging collection. 
"""

import redditDB as rdb

print "Getting all log error types and counts.."

db = rdb.RedditDB("blacksun.cs.mcgill.ca", 31050, "ejacques", "shellcentershell", "reddit_topics")

types = db.log_types()
print 'TYPE', '\t', 'COUNT'
for typ in types:
	print typ, '\t', db.logged_errors_count(typ)
