'''
Script to collect more user activity based. Different from method
 in redditDB in that doesn't rely on mongodb (new textfile system).
 Don't explore users that already exist.
'''

import praw
import time
import os
import requests

userinfo = open('../data/reddit/users/comments.txt').read().splitlines()
userinfo += open('../data/reddit/users/submissions.txt').read().splitlines()

submission_file = open('../data/reddit/users/submissions.txt', 'a')
comment_file = open('../data/reddit/users/comments.txt', 'a')

existing = {}

for line in userinfo:
	name = str(line.split('\t')[0])
	try:
		existing[name] += 1
	except KeyError:
		existing[name] = 1

print "Done collecting existing"

r = praw.Reddit("my fun little user project")

log_interval = 100

def collect():
	counter = 0
	num_users_collected = 0
	num_submissions_collected = 0
	num_comments_collected = 0

	top = r.get_top(limit=900)
	for submission in top:
		try:
			user = submission.author
			try:
				praw_id = user.fullname
			except AttributeError:
				continue

			name = user.name

			if name in existing:
				continue

			existing[name] = 1
			num_users_collected += 1

			print 'new name::', name

			try:
				usubmissions = user.get_submitted()
				ucomments = user.get_comments()
			except requests.exceptions.HTTPError:
				continue

			subs = {}
			comms = {}

			for us in usubmissions:
				subreddit = str(us.subreddit)
				try:
					subs[subreddit] += 1
				except KeyError:
					subs[subreddit] = 1
				num_submissions_collected += 1
			for uc in ucomments:
				subreddit = str(uc.subreddit)
				try:
					comms[subreddit] += 1
				except KeyError:
					comms[subreddit] = 1
				num_comments_collected += 1

			for subreddit, val in subs.iteritems():
				s = name + '\t' + praw_id + '\t' + subreddit + '\t' + str(val) + '\n'
				submission_file.write(s)
			for subreddit, val in comms.iteritems():
				s = name + '\t' + praw_id + '\t' + subreddit + '\t' + str(val) + '\n'
				comment_file.write(s)

			if counter % log_interval == 0:
				print "Num users collected so far:", num_users_collected
				print "Num submissions collected so far:", num_submissions_collected
				print "Num comments collected so far:", num_comments_collected
			counter += 1
		except requests.exceptions.HTTPError:
			continue
		except praw.errors.RedirectException:
			continue

def notification(iter):
	print "#################################################"
	print "Done user collection iteration #", str(iter)
	print "#################################################"
	n = "python notify.py morganeciot@gmail.com 'done iteration #" + str(iter) + " of user collection' VPS"
	os.system(n)

for x in range(100):
	collect()
	notification(x)
	# Sleep for an hour
	time.sleep(3600)