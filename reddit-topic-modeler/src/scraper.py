'''
Methods to pull data from reddit.

TODO: Don't fail with socket error.  
'''

import time
import datetime
import praw
import redditDB as rdb
import errors
import links

class Scraper:

	def __init__(self, useragent, username, password,  host="blacksun.cs.mcgill.ca", port=31050, db="reddit_topics"):
		self.db = rdb.RedditDB(username, password, host, port, db)
		self.reddit = praw.Reddit(useragent)

	'''
	Update topics in the database with the most popular subreddits, capped at a 
	maximum. Default is 2000. 
	'''
	def update_topics(self, max_subreddits=600000):
		subreddits = self.reddit.get_popular_subreddits(limit=max_subreddits)
		for subreddit in subreddits:
			sid = self.db.add_subreddit(subreddit)
			print "adding", subreddit, sid

	'''
	Add random topics. 
	'''
	def add_more_topics(self, max_subreddits=100):
		for x in range(max_subreddits):
			self.db.add_subreddit(self.reddit.get_random_subreddit())


	'''
	Bot method to scrape latest submissions and comments. max_iterations defaults to global
	variable _max_iterations, which is set to 1000. This is the number of times to request
	a set of submissions for each topic from the Reddit server. hot_sleep defaults to the 
	global variable _hot_sleep, which is set to one hour. This is the amount of time to wait
	before requesting a new set of hot submissions. new_sleep defaults to the global variable
	_new_sleep, which is the amount of time to wait before requesting a new set of new 
	submissions, and is set to half an hour.

	Note: This will only scrape topics that are currently in the db. Run update_topics first 
	if want to get new topics, or manually add a topic via RedditDB. 
	'''
	def update_submissions(self, topics=None, max_iterations=10, hot_sleep=3600, submission_limit=900, follow_links=False):
		if submission_limit > 999:
			raise errors.InvalidInput("Calls to Reddit API for submissions will fail after 1000 "
							"so choose submission_limit < 1000.")
		
		#file_num = str(topics).split('/')
		
		if topics is None:
			print "No topics specified. Updating all subreddits."
			docs = self.db.get_subreddits()
		else:
			try:
				topicfile = "../data/" + topics
				topics = open(topicfile).read().splitlines()
				docs = topics
			except IOError:
				print "Cannot find specified topics file."
				return

		### For testing use only 
		#temp = self.db.db["temp"] 	# Will store counts of updates for each subreddit

		#for x in range(max_iterations):	
		#	print "Iteration #"+str(x)+"\n"
		while True:
			for doc in docs:
				if topics is None:
					topic = doc.get("subreddit_name")
				else:
					topic = self.db.subreddit_exists(doc)
					if topic:
						topic = topic.get("subreddit_name")
					else:
						continue

				print "========", topic, ":", datetime.datetime.today(), "========"

				subreddit = self.reddit.get_subreddit(topic)

				hot_count = 0
				#new_count = 0

				# ### For testing use only 
				# try:
				# 	temp_subreddit = temp.find({"name":topic}).limit(1)[0]
				# 	tsid = temp_subreddit.get("_id")
				# 	temp.update( {"_id":tsid}, {"$inc": {"times_visited":1}} )
				# except IndexError:
				# 	tsid = temp.insert({"name":topic, 		#subreddit name
				# 						"times_visited":1,	#num times subreddit has been visited
				# 						"new":0,			#num new submissions
				# 						"revisited":0})		#num revisited submissions
				# 	temp_subreddit = temp.find({"_id":tsid})
					

				try:
					# Get hot submissions
					for submission in subreddit.get_hot(limit=submission_limit):
						print submission
						hot_count += 1

						# Add submission to the database 
						self.db.add_submission(submission, topic, follow_link=follow_links)

						### For testing use only 
						# if sid:
						# 	#print "added at: " + str(time.asctime(time.localtime())) + ' ' + file_num[-1]
						# 	temp.update( {"_id":tsid}, {"$inc": {"new":1}} )
						# else:
						# 	print "seen at: " + str(time.asctime(time.localtime()))
						# 	temp.update( {"_id":tsid}, {"$inc": {"revisited":1}} )

						#print topic+": adding hot #"+str(hot_count), submission, sid

					# Get new submissions
					# for x in range(max_iterations):
					# 	for submission in subreddit.get_new(limit=_submission_limit):
					# 		new_count += 1
					# 		sid = db.add_submission(submission, topic)
					# 		print topic+": adding new #"+str(new_count), submission, sid
					# 	time.sleep(new_sleep)

				except praw.errors.InvalidSubreddit:
					errstr = str(topic)+" is no longer on Reddit."
					self.db.log("InvalidSubreddit", errstr)
				except praw.requests.exceptions.HTTPError as e:
					print "HTTP error", e.message
					self.db.log("HTTPError", e.message)

				print ""
			print "Sleeping for", hot_sleep/60, "minutes"
			time.sleep(hot_sleep)

	'''
	This method is used to go through all submissions in the database and update 
	them with the html content of the link associated with the suggestion. 
	sub_per_topic specifies the number of submissions to update per subreddit. 
	If this number is small, all of the subreddits can quickly acquire some link content. 
	''' 
	def update_submission_content(self, topics=None, sub_per_topic=10):
		if topics is None:
			print "No topics specified. Updating all subreddits."
		else:
			try:
				topicfile = "../data/" + topics
				topics = open(topicfile).read().splitlines()
			except IOError:
				print "Cannot find specified topics file."
				return

		while True:
			# Go through each subreddit in db or specified by topic list 
			if topics:
				subreddits = topics
			else:
				subreddits = self.db.get_subreddits()
			for subreddit in subreddits:
				if topics:
					subreddit = self.db.subreddit_exists(subreddit)
					if not subreddit:
						continue

				topic = subreddit.get("subreddit_name")
				print "========", topic, "========"

				num_content = 0
				# Only get the submissions whose (non-empty) urls haven't been scraped
				for submission in self.db.empty_submissions(topic):
					link = submission.get("url")
					
					try:
						link = str(link)
					except UnicodeEncodeError:
						continue

					html = links.scrape_link(str(link), topic)
					if html:
						print "Adding content from:", link
						html = str(html)
						num_content += 1
					
					self.db.add_link_content(submission.get("_id"), html)

					if num_content >= sub_per_topic:
						break

				print "Crawled", num_content, "links for", topic, datetime.datetime.today()

