"""
Script to find metadata (parameters) used for a 
particular llda file. 
"""

import sys
import string
import redditDB

filename = sys.argv[1]

oid = filename.split("_")[2].split('.')[0]

rdb = redditDB.RedditDB()

metadata = rdb.get_metadata(oid)
for key,val in metadata.iteritems():
	print string.upper(key),":",val