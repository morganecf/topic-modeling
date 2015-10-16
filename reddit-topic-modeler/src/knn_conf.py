import json
from StringIO import StringIO

import distances as d
import errors

"""
TODO: Make sure can leave blank for defaults. 
"""

class KNNConf:

	def __init__(self, pathname):
		try:
			io = StringIO("../data/"+pathname)
			conf = json.load(io)
		except ValueError:
			raise errors.InvalidConf("Conf file could not be found." 
				+ "Conf file should be in data directory.")

		if check_topics(conf.get("topics")):
			self.topics = conf.get("topics")
		else:
			raise errors.InvalidConf("Topics should be a list of strings.")

		try:
			self.distance = getattr(d, conf.get("distance"))
		except AttributeError:
			raise errors.InvalidConf("%s is not a valid distance function.", conf.get("distance"))

		if check_ints(conf.get("k")):
			self.k = conf.get("k")
		else:
			raise errors.InvalidConf("k should be a positive integer.")

		if check_ints(conf.get("docs_used")):
			self.num_docs = conf.get("docs_used")
		else:
			raise errors.InvalidConf("docs_used should be a positive integer.")



def check_topics(topics):
	b1 = type(topics) == list
	b2 = all(map(lambda topic: type(topic) == str, topics))
	return b1 and b2

def check_ints(i):
	return type(i) == int and i >= 1
