'''
Takes an input file of praw ids and collects the comments for these.
'''

import os
import sys
import time
import praw
from datetime import datetime

base_dir = os.path.join("..", "data", "reddit")

def make_dir(d):
	path = os.path.join(base_dir, d)
	exit_code = os.system("mkdir -p " + path)
	return exit_code == 0

# Open a file in append or write mode as necessary
def open_file(path, fname):
	full_path = os.path.join(base_dir, path, fname)
	try:
		f = open(full_path, 'a')
	except IOError:
		f = open(full_path, 'w')
	return f

reddit = praw.Reddit(user_agent="my super fun project")

try:
	fname = sys.argv[1]
except IndexError:
	print "Must provide a praw id file."
	sys.exit(1)

praw_ids = open(fname).read().splitlines()
num_ids = len(praw_ids)

num_comments = 0
counter = 0
num_dumps = 0

data_buffer = {}
chunk_size = 10000
log_interval = 10

start = time.time()

# Collect submissions
for praw_id in praw_ids:

	# Get corresponding submission
	sub = reddit.get_submission(submission_id=praw_id)

	# Get corresponding subreddit
	try:
		subreddit = str(sub.subreddit)
	except AttributeError:
		continue

	# Get date associated submission was created
	try:
		created = sub.created
	except AttributeError:
		continue

	if type(created) == float:
		date = datetime.fromtimestamp(created)
	elif type(created) == datetime:
		date = created
	else:
		continue

	year = str(date.year)
	month = str(date.month)
	day = str(date.day)

	# Create/find path where info should be stored
	path = os.path.join(subreddit[0].lower(), subreddit, year, month, day)
	make_dir(path)

	# Get associated submission text
	try:
		text = sub.selftext.strip() or ''
	except AttributeError:
		text = ''

	# Get comments themselves
	try:
		comments = sub.comments
	except AttributeError:
		comments = None

	# Just store submission text with comments, since only getting top-tier comments
	if comments:
		comment_info = text
		for comment in comments:
			try:
				comment_info += comment.body
				num_comments += 1
			except AttributeError:
				continue

		comment_str = ' '.join(comment_info.split()).strip()
		if comment_str:
			data = (praw_id + '\t' + comment_str + '\n').encode('utf8')

			try:
				data_buffer[path].append(data)
			except KeyError:
				data_buffer[path] = [data]

	if len(data_buffer) >= chunk_size:
		# Write data to files
		for path, data in data_buffer.iteritems():

			comments_file = open_file(path, 'comments0.txt')

			for data_item in data:
				comments_file.write(data_item)

			comments_file.close()

		num_dumps += 1

		# Clear buffer
		data_buffer = {}

	if counter % log_interval == 0:
		print "Comment Collection Progress:", counter, "comment sets collected out of", num_ids, (counter / float(num_ids)) * 100, "%"
		print "Num paths in buffer so far:", len(data_buffer)
		print "Num comments total so far:", num_comments
		print "Number of dumps to file so far:", num_dumps
		print "Time spent:", (time.time() - start) / 60.0, "minutes"
		print ""

	counter += 1