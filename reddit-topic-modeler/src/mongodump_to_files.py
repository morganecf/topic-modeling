"""
Convert mongodumps to text files in the following dir structure:

/first char
	/subreddit
		/year
			/month
				/day
					submissions.txt (object id \t praw id \t title/text)
						note: praw_id of -1 means none was found. probably rare
					comments.txt (submission object id \t text_layer1, text_layer2, text_layer3...))
					urls.txt (submission object id \t url)
					xposts.txt (submission object id \t xpost)
					subdomains.txt (submission object id \t subdomain)

					For wayback:
					comments0.txt (got only top level comments)
					domains.txt (praw does it for you)

users dir
	submissions.txt
	comments.txt
	format: username, object id, <list of subreddits contributed to, with weights>
	lines correspond ?
	**fix for $
"""

import os
import sys
import time
import json
import utils
from datetime import datetime

base_dir = os.path.join("..", "data", "reddit")

chunk_size = 5000
log_interval = 5000

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

# Get subreddit id to name mappings
subreddit_ids = {}
srlines = open("../data/subreddit_to_id.txt").read().splitlines()
for line in srlines:
	try:
		sr, sid = line.split("\t")
	except ValueError:
		print "Subreddit doesn't have id?", line
		continue
	subreddit_ids[sid] = sr.strip()

print "Done subreddit id mapping:", len(subreddit_ids), "subreddits"

# Dump submissions/comments/etc
def dump_submission_info(sub_path):

	start = time.time()

	# Log useful info
	num_submissions = 7333071

	counter = 0
	num_dumps = 0
	num_urls_found = 0
	num_xposts_found = 0

	# Will store chunks of data to write and cleared at certain intervals
	# to avoid too much I/O.
	data_buffer = []

	# Collect submissions
	with open(sub_path) as submission_file:
		for submission_raw in submission_file:

			submission = json.loads(submission_raw)

			# Get year, month, day
			tmstp = submission.get("created")
			if type(tmstp) == int:
				date = datetime.fromtimestamp(tmstp)
			elif type(tmstp) == datetime:
				date = tmstp
			else:
				print "WARNING::::different date format found", type(tmstp), tmstp
				continue

			try:
				sid = submission.get("subreddit_id").values()[0]
				subreddit = subreddit_ids[sid]
			except KeyError:
				print "WARNING::::subreddit id not found:", submission
				continue

			year = str(date.year)
			month = str(date.month)
			day = str(date.day)

			path = os.path.join(subreddit[0].lower(), subreddit, year, month, day)
			make_dir(path)

			# Extract relevant pieces of information
			submission_id = str(submission.get("_id").values()[0])
			submission_title = submission.get("submission_title") or ''
			submission_text = submission.get("submission_text") or ''
			submission_prawid = submission.get("praw_id") or '-1'

			# Create information to write to file
			submission_info = submission_id + "\t" + submission_prawid + "\t" + submission_title + " " + submission_text
			url_info = submission.get("url") or ''
			xpost_info = utils.extract_subreddit_xpost(submission_title) or utils.get_internal_link(url_info)

			# Create data object and store in buffer
			data = {'submissions': (submission_info + '\n').encode("utf8")}
			if url_info:
				data['urls'] = (submission_id + '\t' + url_info + '\n').encode("utf8")
			if xpost_info:
				data['xposts'] = (submission_id + '\t' + xpost_info + '\n').encode("utf8")

			data_buffer.append((path, data))

			# Write data and clear buffer every <chunk_size> submissions
			if len(data_buffer) >= chunk_size:

				filehandlers = {}
				for path, data in data_buffer:
					try:
						# See if file handlers have already been initialized
						fhs = filehandlers[path]
						for fh_type, fh in fhs.iteritems():
							if fh_type in data:
								fh.write(data[fh_type])
					except KeyError:
						# Otherwise create the file handlers and write to them
						fhs = {'submissions': open_file(path, 'submissions.txt')}
						fhs['submissions'].write(data['submissions'])
						if data.get('urls'):
							fhs['urls'] = open_file(path, 'urls.txt')
							fhs['urls'].write(data['urls'])
						if data.get('xposts'):
							fhs['xposts'] = open_file(path, 'xposts.txt')
							fhs['xposts'].write(data['xposts'])
						filehandlers[path] = fhs

				# Now close all file handlers
				for path, fhs in filehandlers.iteritems():
					for fh_type, fh in fhs.iteritems():
						fh.close()

				# Clear buffer
				data_buffer = []
				num_dumps += 1

			if counter % log_interval == 0:
				print "Progress:", counter, "submissions dumped out of", num_submissions, (counter / float(num_submissions)) * 100, "%"
				print "\tNumber of URLs found so far:", num_urls_found
				print "\tNumber of xposts found so far:", num_xposts_found
				print "\tNumber of dumps to file so far:", num_dumps
				print "\tTime spent:", (time.time() - start) / 60.0, "minutes"
				print ""
			counter += 1

def dump_comments(comm_path):
	num_comments = 57334890

	start = time.time()

	counter = 0
	num_dumps = 0

	# Will store chunks of data to write and cleared at certain intervals
	# to avoid too much I/O.
	data_buffer = {}

	# Collect submissions
	with open(comm_path) as comment_file:
		for comment_raw in comment_file:

			comment = json.loads(comment_raw)

			# Get year, month, day
			tmstp = comment.get("created")
			if type(tmstp) == int:
				date = datetime.fromtimestamp(tmstp)
			elif type(tmstp) == datetime:
				date = tmstp
			else:
				print "WARNING::::different date format found", type(tmstp), tmstp
				continue

			try:
				sid = comment.get("topic_id").values()[0]
				subreddit = subreddit_ids[sid]
			except KeyError:
				print "WARNING::::subreddit id not found:", submission
				continue
			except AttributeError:
				print "no vals?", comment
				break

			year = str(date.year)
			month = str(date.month)
			day = str(date.day)

			path = os.path.join(subreddit[0].lower(), subreddit, year, month, day)
			make_dir(path)

			# Extract relevant pieces of information
			comment_id = str(comment.get("_id").values()[0])
			submission_id = comment.get("submission_id").values()[0]
			comment_text = comment.get("comment_text") or ''
			layer = str(comment.get("layer"))

			# Create information to write to file
			comment_info = (comment_id + '\t' + submission_id + '\t' + layer + '\t' + comment_text + '\n').encode("utf8")

			try:
				data_buffer[path].append(comment_info)
			except KeyError:
				data_buffer[path] = [comment_info]

			# Write data and clear buffer every <chunk_size> submissions
			if len(data_buffer) >= chunk_size:

				for path, data in data_buffer.iteritems():
					f = open_file(path, "comments.txt")
					for comment in data:
						f.write(comment)
					f.close()

				# Clear buffer
				data_buffer = {}
				num_dumps += 1

			counter += 1
			if counter % log_interval == 0:
				print "Progress:", counter, "comments collected out of", num_comments, (counter / float(num_comments)) * 100, "%"
				print "\tNumber of dumps to file so far:", num_dumps
				time_spent = (time.time() - start) / 60.0
				print "\tTime spent:", time_spent, "minutes"
				print "\tExpected time remaining:", (num_comments - counter) / (counter / time_spent), "minutes"
				print ""


# Dump wayback submissions
def dump_wayback_submission_info(sub_path):
	start = time.time()

	# Log useful info
	num_submissions = 18609213
	counter = 0
	num_dumps = 0
	num_urls_found = 0
	num_xposts_found = 0
	num_domains_found = 0
	num_no_date = 0

	# Will store chunks of data to write, cleared at certain intervals
	# to avoid too much I/O.
	data_buffer = {}

	# Will store chunks of data specifically for comment file, used to
	# scrape later comments.
	comment_file = open(os.path.join('..', 'data', 'reddit', 'wayback_comments_to_scrape.txt'), 'w')
	comment_buffer = []

	# Collect submissions
	with open(sub_path) as submission_file:
		for submission_raw in submission_file:

			submission = json.loads(submission_raw)

			# Get year, month, day
			try:
				tmstp = submission.get("created").values()[0]
			except AttributeError:
				print "WARNING::::no timestamp?", submission.get("created")
				continue
			if type(tmstp) == int:
				date = datetime.fromtimestamp(tmstp / 1000)
			elif type(tmstp) == datetime:
				date = tmstp
			else:
				num_no_date += 1
				continue

			if submission.get("comment_url"):
				subreddit = utils.get_internal_link(submission.get("comment_url"))
				if not subreddit:
					continue
			# Ignore ones that don't have associated subreddit
			else:
				continue

			year = str(date.year)
			month = str(date.month)
			day = str(date.day)

			path = os.path.join(subreddit[0].lower(), subreddit, year, month, day)
			make_dir(path)

			# Extract relevant pieces of information
			submission_id = str(submission.get("_id").values()[0])
			submission_title = submission.get("submission_title") or ''
			submission_prawid = submission.get("reddit_id") or '-1'

			# Create information to write to file
			submission_info = submission_id + "\t" + submission_prawid + "\t" + submission_title
			url_info = submission.get("url") or ''
			domain_info = submission.get("domain")

			# Get potential xpost info
			xpost_info = utils.extract_subreddit_xpost(submission_title)
			if not xpost_info:
				if domain_info.startswith("self."):
					internal = domain_info.split(".")[1]
					if internal != subreddit:
						xpost_info = internal

			# Create data object and store in buffer
			data = {'submissions': (submission_info + '\n').encode("utf8")}
			if url_info:
				data['urls'] = (submission_id + '\t' + url_info + '\n').encode("utf8")
				num_urls_found += 1
			if xpost_info:
				data['xposts'] = (submission_id + '\t' + xpost_info + '\n').encode("utf8")
				num_xposts_found += 1
			if domain_info:
				data['domains'] = (submission_id + '\t' + domain_info + '\n').encode("utf8")
				num_domains_found += 1

			try:
				data_buffer[path].append(data)
			except KeyError:
				data_buffer[path] = [data]

			# Store information about comments for later scraping
			if submission_prawid != '-1':
				comment_buffer.append((path, submission_prawid))

			# Write data and clear buffer every <chunk_size> submissions
			if len(data_buffer) >= chunk_size:

				# Only ever open 5 files at a time
				for path, data in data_buffer.iteritems():
					# Open files associated with this path
					filehandlers = {'submissions': open_file(path, 'submissions.txt'),
									'urls': open_file(path, 'urls.txt'),
									'xposts': open_file(path, 'xposts.txt'),
									'domains': open_file(path, 'domains.txt')}

					# Write data to files
					for data_item in data:
						if data_item.get('urls'):
							filehandlers['urls'].write(data_item['urls'])
						if data_item.get('xposts'):
							filehandlers['xposts'].write(data_item['xposts'])
						if data_item.get('domains'):
							filehandlers['domains'].write(data_item['domains'])

					# Now close files
					filehandlers['submissions'].close()
					filehandlers['urls'].close()
					filehandlers['xposts'].close()
					filehandlers['domains'].close()

				# Update comment file
				for path, pid in comment_buffer:
					comment_file.write(path + '\t' + pid + '\n')

				# Clear buffer
				data_buffer = {}
				comment_buffer = []
				num_dumps += 1

			counter += 1
			if counter % log_interval == 0:
				print "Wayback Progress:", counter, "submissions dumped out of", num_submissions, (counter / float(num_submissions)) * 100, "%"
				print "\tNumber of URLs found so far:", num_urls_found
				print "\tNumber of xposts found so far:", num_xposts_found
				print "\tNumber of dumps to file so far:", num_dumps
				print "\tNumber with no date:", num_no_date
				time_spent = (time.time() - start) / 60.0
				print "\tTime spent:", time_spent, "minutes"
				print "\tExpected time remaining:", (num_submissions - counter) / (counter / time_spent)
				print ""

	comment_file.close()

# Dump user activity information
def dump_user_info(rdb):

	make_dir('users')

	submission_file = open(os.path.join(base_dir, 'users', 'submissions.txt'), 'w')
	comment_file = open(os.path.join(base_dir, 'users', 'comments.txt'), 'w')

	num_users = rdb.num_users()
	counter = 0
	log_interval = 10

	start = time.time()

	for user in rdb.get_users():
		# Write submission information
		if user.get("submissions"):
			for subreddit, count in user[u"submissions"].iteritems():
				# Account for accidental $-key
				if subreddit == '$':
					for k, v in user[u"submissions"]["$"].iteritems():
						s = user.get("name") + '\t' + user.get("praw_id") + '\t' + k + "\t" + str(v) + "\n"
						submission_file.write(s)
				s = user.get("name") + '\t' + user.get("praw_id") + '\t' + subreddit + "\t" + str(count) + "\n"
				submission_file.write(s)

		# Write comment information
		if user.get("comments"):
			for subreddit, count in user[u"comments"].iteritems():
				# Account for accidental $-key
				if subreddit == '$':
					for k, v in user[u"comments"]["$"].iteritems():
						s = user.get("name") + '\t' + user.get("praw_id") + '\t' + k + "\t" + str(v) + "\n"
						comment_file.write(s)
				s = user.get("name") + '\t' + user.get("praw_id") + '\t' + subreddit + "\t" + str(count) + '\n'
				comment_file.write(s)

		if counter % log_interval == 0:
			print counter, (time.time() - start) / 60.0, (counter / float(num_users)) * 100, "%"

		counter += 1

	submission_file.close()
	comment_file.close()

dt = sys.argv[1]
if dt == 'user':
	dump_user_info('../mongodump/users.json')
elif dt == 'wayback':
	dump_wayback_submission_info('../mongodump/wayback_submissions.json')
elif dt == 'submissions':
	dump_submission_info("../mongodump/submissions.json")
elif dt == 'comments':
	dump_comments("../mongodump/comments.json")
else:
	print "Please choose one of: wayback, submissions, comments, user"
	sys.exit(1)
