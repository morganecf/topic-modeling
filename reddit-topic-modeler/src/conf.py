import json

import errors
import redditDB as rdb
from utils import __stringlist__, __positive__, __nonnegative__, __stopwords__, __distance__, __file__, __boolean__

"""
Class to model configuration file, which has 
parameters used to build models. Default values
are automatically filled in by ConfDict object
when empty sequences/negative ints are encountered
as parameters.  
"""

class Conf:

	def __init__(self, pathname):
		try:
			conf_file = open("../data/conf_files/"+pathname, "rt")
		except IOError:
			raise errors.InvalidConf("Conf file could not be found. " 
				+ "Conf file should be in data directory.")
		try:
			#io = StringIO(conf_file)
			#temp_conf = json.load(io)
			conf = json.load(conf_file)
		except ValueError:
			raise errors.InvalidConf("Conf file does not contain " + 
				"valid JSON.")

		# Database parameters
		try:
			#db_params = temp_conf["database"]
			db_params = conf["database"]
			if db_params == {}:				# Assume localhost
				self.db = rdb.RedditDB('ejacques','shellcentershell','blacksun.cs.mcgill.ca', 31050, 'reddit_topics')
			else:
				host = db_params.get("host")
				port = db_params.get("port")
				username = db_params.get("username")
				password = db_params.get("password")
				dbname = db_params.get("db")
				self.db = rdb.RedditDB(host=host, port=port, username=username, password=password, db=dbname)
		except KeyError:
			raise errors.InvalidConf("Conf file should have a database "
				+ "connection parameter dictionary.")

		# Topics should be list of string subreddits 
		self.topics = __stringlist__(conf.get("topics"), "topics")

		# Number of documents used per topic 
		self.num_docs = __positive__(conf.get("docs_per_topic"), "docs_per_topic")

		# Comment level at which to stop 
		self.comment_level = __nonnegative__(conf.get("comment_level"), "comment_level")

		# Removing words that occur with certain frequency
		self.removal_threshold = __positive__(conf.get("removal_threshold"), "removal_threshold")

		# Removing words that occur across certain % of documents 
		self.removal_perc = __positive__(conf.get("removal_perc"), "removal_perc")

		# Maximum and minimum word length to keep
		self.max_word_length = __positive__(conf.get("max_word_length"), "max_word_length")
		self.min_word_length = __nonnegative__(conf.get("min_word_length"), "min_word_length")

		# Type of stopword list to use 
		self.stopwords = __stopwords__(conf.get("stopwords"), "stopwords")

		# Whether or not to stem 
		self.stem = __boolean__(conf.get("stem"), "stem")

		# Dimensionality of word vector
		self.dimensionality = __positive__(conf.get("dimensionality"), "dimensionality")

		# Whether or not to apply dimensionality reduction using LSA
		self.lsi = __boolean__(conf.get("lsi"), "lsi")

		''' For LDA ''' 

		# Pointer to pre-serialized data file to use to directly build model
		# I.e., no need to access reddit db  
		# self.corpus_path = __file__("../data/"+conf.get("serialized_corpus"), "corpus")

		# # Pointer to vocab dictionary 
		# # I.e., no need to access reddit db 
		# self.vocabulary_path = __file__("../data/"+conf.get("data"), "data")

		''' For KNN '''

		# Number of nearest neighbors (for KNN)
		self.k = __positive__(conf.get("k"), "k")

		# Distance function (for KNN)
		self.distance = __distance__(conf.get("distance"), "distance")

