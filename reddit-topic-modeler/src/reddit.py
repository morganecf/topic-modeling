'''
Defines Reddit objects.
'''

import redditDB as db
import preprocessors

# HARDCODE FOR NOW BUT WILL HAVE TO CHANGE HOW THIS IS INCORPORATED 
rdb = db.RedditDB(host="blacksun.cs.mcgill.ca", port="31050", username="mciot", password="", db="reddit_topics")

class RedditTopic:

	def __init__(self, topicJson):
		self.name = topicJson.get("subreddit_name")

	'''
	Lazy. Returns generator for a subreddit's submissions
	for between a daterange.  
	'''
	def get_submissions(self, limit=None, start=None, stop=None):
		cursor = rdb.submission_list(self.name)
		for obj in cursor:
			yield RedditSubmission(obj)

class RedditObject:

	def __init__(self, objectJson):
		self.topic = objectJson.get("topic")
		self.karma = objectJson.get("karma")
		self.downvotes = objectJson.get("downvotes")
		self.rid = objectJson.get("_id")
		self.created = objectJson.get("created")
	
	'''
	TODO Convert to datetime object.
	'''
	def get_date(self): return self.created


	'''
	Comparison functions defined on comments and submissions.  
	'''
	def _byDate(self, other): return self.get_date() > other.get_date()

	def _byKarma(self, other): return self.karma > other.karma

	# def __eq__(self, other):
	# 	return isinstance(other, RedditObject) and 


class RedditSubmission(RedditObject):

	def __init__(self, submissionJson):
		RedditObject.__init__(self, submissionJson)
		self.title = submissionJson.get("submission_title")
		self.text = submissionJson.get("submission_text")
		self.num_comments = submissionJson.get("num_comments")
		self.flair = submissionJson.get("flair")
		self.url = submissionJson.get("url")

	'''
	Lazy. Returns generator of a submission's comments.
	Can specify the level of the comment tree to stop at. 
	Superfluous??? 
	'''
	def get_comments(self, level_thresh):
		cursor = rdb.comment_list(self.rid)
		for obj in cursor:
			if level_thresh:
				if obj.get("level") <= level_thresh:
					yield RedditComment(obj)
			else:
				yield RedditComment(obj)


class RedditComment(RedditObject): 

	def __init__(self, commentJson):
		RedditObject.__init__(self, commentJson)
		self.submission = commentJson.get("submission_id")
		self.text = commentJson.get("comment_text")
		self.level = commentJson.get("level")
		self.num_embedded_comments = commentJson.get("num_sub_comments")
		self.gold = commentJson.get("gold")


class RedditDocument:

	def __init__(self, submission, topicstr, comment_level=None):
		self.topic = topicstr
		self.level_thresh = comment_level
		self.submission = submission
		self.comments = self.get_comments()
		self.pure_text = self.raw_text()

		# Extract links 
		if submission.url:
			self.websites = preprocessors.extract_websites(self.pure_text + ' ' + submission.url)
		else:
			self.websites = preprocessors.extract_websites(self.pure_text)

		# Extract references to other subreddits
		self.references = preprocessors.extract_references(self.pure_text)
		self.words = None	# List of words w

	def get_comments(self):
		comments = []
		for comment in self.submission.get_comments(self.level_thresh):
			comments.append(comment)
		return comments

	# Get all the text input from the doc. up_to_layer excludes the 
	# comments that are at a certain layer in the comment tree. 
	def raw_text(self):
		comment_text = ""
		for comment in self.comments:
			comment_text += comment.text + " "
		return self.submission.title + " " + self.submission.text + " " + comment_text

	def get_words(self, newtext):
		self.words = newtext.split()



