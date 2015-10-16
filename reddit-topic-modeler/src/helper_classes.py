from errors import InvalidConf 

class RedditCorpus(object):
	"""
	Wrapper class for a presaved corpus to 
	be more memory-friendly. 
	"""

	def __init__(self, dictionary, text):
		if isinstance(text, basestring):
			try:
				self.text = open("../data/dictionaries/"+text)
				self.pre_split = False
			except IOError:
				raise IOError("Could not find corpus %s.", text)
		else:
			self.text = text
			self.pre_split = True		
		self.dictionary = dictionary

	# Assumes that each document is on one line and that
	# words have already been preprocessed and separated
	# by whitespace 
	def __iter__(self):
		for line in self.text:
			if self.pre_split:
				yield self.dictionary.doc2bow()
			else:
				yield self.dictionary.doc2bow(line.split())

class ConfDict(dict):
	"""
	Subclasses dict to allow for automatic setting of 
	default parameter. 
	"""

	def __init__(self, **args):
		dict.__init__(args)

		self.defaults = {"topics":[],						# Will indicate to use all topics 
						"docs_used":0,						# Use all docs
						"comment_level":None,				# Use all comments 
						"removal_threshold":0,				# Don't remove any words with any frequency
						"removal_perc":0,					# Don't remove any words that occur across certain % of docs
						"stopwords":"long",					# Default is to use more comprehensive stopword list
						"max_word_length":None,				# Default is to use all words 
						"min_word_length":None,
						"distance":"cosine",
						"k":0,								# Will indicate to use k based on function of number of topics 
						"data":None,
						"serialized_corpus":None}

	def __getitem__(self, key):
		val = dict.__getitem__(self, key)
		# If value is a non-negative int, keep
		if isinstance(val, int) and val > -1:
			return val
		# If value is a non-empty list/string, keep
		if (isinstance(val, basestring) or isinstance(val, list)) and len(val) > 0:
			return val
		# Otherwise set to default value 
		try:
			self[key] = self.defaults[key]
			return self[key]
		except KeyError:
			raise InvalidConf("%s should not be a parameter.", val)

	def __setitem__(self, key, val):
		dict.__setitem__(self, key, val)

