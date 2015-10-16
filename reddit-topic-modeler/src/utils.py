'''
Some utility methods. 
'''

import os 
import re
import string
import random 
import fnmatch
import operator
import distances
import defaultdict
import preprocessors 
from praw import objects
from errors import InvalidConf
from helper_classes import ConfDict

# Used for supplying default values in empty conf file 
DEFAULTS = {"topics": [],                        # Will indicate to use all topics 
            "docs_per_topic": 0,                 # Use all docs
            "comment_level": None,               # Use all comments 
            "removal_threshold": 0,              # Don't remove any words with any frequency
            "removal_perc": 0,                   # Don't remove any words that occur across certain % of docs
            "stopwords": "long",                 # Default is to use more comprehensive stopword list
            "max_word_length": None,             # Default is to use all words 
            "min_word_length": None,
            "stem": False,
            "dimensionality": 500,               # 200-500 is considered golden standard, choose upper bound 
            "lsi": True,          
            "distance": "cosine",
            "k": 0,                              # Will indicate to use k based on function of number of topics 
            "data": None,
            "serialized_corpus": None
            }


def layer_comments(tree):
    """
    Flatten a nested tree of comments into a dictionary where each key represents the 
    layer the comment was found in. For now ignore the more comments thing. 

    TODO: What to do about more comments? 
    """
    layer = tree[:]
    levels = {}
    level = 0
    while layer:
        only_comments_layer = filter(lambda comment: type(comment) == objects.Comment, layer)
        levels[level] = only_comments_layer
        next_layer = flatten(map(lambda comment: comment.replies, only_comments_layer))
        layer = next_layer[:]
        level += 1
    return levels

def flatten(l):
    """
    Flatten a two-dimensional list.
    """
    f = []
    for item in l:
        f.extend(item)
    return f


# Probably deprecated 
def replies(obj):
    """
    Returns replies if they are available. Otherwise might be a MoreComment object,
    in which case just return empty list for now. 
    """
    try:
        return obj.replies
    except AttributeError:
        return []

# Match the domain 
domain_regex = re.compile(r"(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?")

# Match subreddit from a within-reddit url 
internal_url_regex = re.compile(r"http://www\.reddit\.com/r/([^/]+)/")

popular_domains = {'youtu.be': 'youtube.com', 'i.imgur.com': 'imgur.com'}

def normalize_domain(domain):
	return popular_domains.get(domain) or domain

def get_domain(url):
	"""
	Extract domain name from a url.
	"""
	match = re.match(domain_regex, url)
	if match:
		domain = match.groups()[1].replace("www.", "").replace("m.", "")
		if domain in popular_domains:
			return popular_domains[domain]
		return domain

def is_internal(url):
	return get_domain(url) == "reddit.com"

def get_internal_link(url):
	"""
	Extract subreddit from a url pointing to reddit.
	"""
	match = re.match(internal_url_regex, url)
	if match:
		return match.groups()[0]

def domain_frequencies(documents):
    """
    Given set of documents, creates a dict with frequency count of each domain 
    (in url) found in documents. 
    """
    domains = defaultdict(int)
    for doc in documents:
        if doc.get("url"):
            domain = get_domain(doc.get("url"))
            domains[domain] += 1
    return domains

def top_domains(frequencies, top=None):
    """
    Given a dictionary of domain frequencies, sorts the dict 
    and returns the top "top" domains, if top is specified. Otherwise 
    returns all of them. 
    """
    sorted_freqs = sorted(frequencies.iteritems(), key=operator.itemgetter(1), reverse=True)
    if top:
        return sorted_freqs[:top]
    return sorted_freqs

def extract_subreddit_xpost(title):
	"""
    Given the title of a submission, extract potential crosspost subdomain. 
    Almost all xpost titles take the form (xpost <subreddit>), where <subreddit> may
    or may not have /r/, or the parentheses may have another bracket form like {} or [].
    """
	if 'xpost' not in title:
		return
	# Get the single word after "xpost", after removing "from"
	try:
		subreddit = title.lower().split("xpost")[1].replace("from", "")
		subreddit = subreddit.split()[0]
	except IndexError:
		return
	# Remove r/
	subreddit = subreddit.replace("r/", "")
	# Now remove all punctuation
	try:
		subreddit = str(subreddit).translate(None, string.punctuation)
		return subreddit
	except UnicodeEncodeError:
		return None

def submission_date_range(documents):
    """
    Gets the date range of set of documents at the submission level. 
    """
    dates = [doc.submission.created for doc in documents]
    if len(dates) == 0:
        return -1, -1
    return min(dates), max(dates)


def comment_date_range(documents):
    """
    Gets the date range of a set of documents at the comment level. 
    """
    dates = []
    for doc in documents:
        dates.extend([comment.created for comment in doc.comments])
    if len(dates) == 0:
        return -1, -1
    return min(dates), max(dates)

def partition(documents, percentage):
    """
    Splits a set of documents into train and test sets based on percentage, 
    which indicates proportion of documents that should go in train set. 
    """
    train = []
    n = int(percentage * len(documents))
    docs = documents[:]
    for x in range(n):
        doc = random.choice(docs)
        docs.remove(doc)
        train.append(doc)
    print len(train), len(docs)
    return train, docs

def is_default(x):
    """
    Checks if conf param isn't supplied (need default val).
    -1, "", or [] indicate defaults should be used. 
    """
    return x == -1 or x == "" or x == []

def __stringlist__(l, key):
    """
    Verifies that a conf param is list of strings. 
    """
    if is_default(l):
        return DEFAULTS[key]
    b1 = type(l) == list
    b2 = all(map(lambda x: isinstance(x, basestring), l))
    if b1 and b2:
        return l
    raise InvalidConf("%s should be a list of strings.", key)

def __positive__(i, key):
    """
    Verifies that a conf param is positive int. 
    """
    if is_default(i):
        return DEFAULTS[key]
    if type(i) == int and i >= 1:
        return i 
    raise InvalidConf("%s should be a positive integer.", key)

def __nonnegative__(i, key):
    """
    Verifies that a conf param is non-negative int. 
    """
    if is_default(i):
        return DEFAULTS[key]
    if type(i) == int and i >= 0:
        return i
    raise InvalidConf("%s should be a non-negative integer.", key)

def __string__(s, key):
    """
    Verifies that a conf param is a string. 
    """
    if is_default(s):
        return DEFAULTS[key]
    if isinstance(s, basestring):
        raise InvalidConf("%s should be a string.", key)

def __distance__(d, key):
    """
    Verifies that conf param is correct distance fn for KNN.
    """
    if is_default(d):
        return DEFAULTS[key]
    try:
        return getattr(distances, d)
    except AttributeError:
        raise InvalidConf("%s is not a valid distance function.", d)

def __stopwords__(sw, key):
    """
    Verifies that conf stopwords param is valid. 
    """
    if is_default(sw):
        return DEFAULTS[key]
    if sw == "long" or sw == "short":
        return sw
    raise InvalidConf("Stopwords used should be specified by either 'long' or 'short.'")

def __file__(f, key):
    """
    Verifies that a data file exists. 
    """
    if is_default(f):
        return DEFAULTS[key]
    try:
        open(f)
        return f
    except IOError:
        raise InvalidConf("Could not find data file %s.", f)

def __boolean__(b, key):
    """
    Verifies that a conf param is a boolean. 
    """
    if is_default(b):
        return DEFAULTS[key]
    if type(b) == bool:
        return b
    raise InvalidConf("%s should be true or false.", key)

def createConfDict(dictionary):
    """
    Creates a conf dictionary type from given dictionary. 
    """
    d = ConfDict()
    for key, val in dictionary.iteritems():
        d[key] = val
    return d

def createMetaData(conf):
    """
    Creates metadata to store in mongodb from the given conf file. This essentially 
    creates a new conf file with the user-input values and the default values if none 
    were specified. 
    """
    if not conf.topics:
        topics = list(conf.db.subreddit_list())
    else:
        topics = conf.topics
    try:
        data = conf.data
    except AttributeError:
        data = None
    try:
        corpus = conf.serialized_corpus
    except AttributeError:
        corpus = None

    metadata = {"topics": topics,
                "docs_per_topic": conf.num_docs,
                "comment_level": conf.comment_level,
                "removal_threshold": conf.removal_threshold,
                "removal_perc": conf.removal_perc,
                "stopwords": conf.stopwords,
                "max_word_length": conf.max_word_length,
                "min_word_length": conf.min_word_length,
                "stem": conf.stem,
                "dimensionality": conf.dimensionality,
                "lsi": conf.lsi,
                "distance": conf.distance,
                "k": conf.k,
                "data": data,
                "serialized_corpus": corpus } 
    return metadata 

def name_file(path):
    """
    Appends a number to a file name if file with same pathname already exists. 
    NOTE: Won't work on windows. 
    """
    path_parts = path.split('/')
    filename = path_parts[-1]
    directory = '/'.join(path_parts[:len(path_parts)-1])+'/'
    file_parts = filename.split('.')
    pattern = file_parts[0]+'_[0-9]*.'+file_parts[1]
    matches = fnmatch.filter(os.listdir(directory), pattern)
    # If found some matches, append a number
    if len(matches) > 0:
        num = matches[-1].split('.')[0][-1]
        return directory + file_parts[0] + '_' + str(int(num)+1) + '.' + file_parts[1]
    # Otherwise return the orgiinal file path 
    print path


def clean(text, uni):
    # If it's a retweet, get rid of the RT text (might as well)
    if 'RT @' in text:
        text = re.sub('RT @\w+?:? ', '', text)
    if 'RT: ' in text:
        text = text.replace('RT: ', '')
    text = text.lower()
    # Now get rid of the URLs starting with http:// (links appear shortened so, no https)
    text = re.sub(r'[ ]*http:\/\/[^ ]+', '', text)
    # Now replace some HTL entities
    replacements = {
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
        ':': ''
    }
    # Get rid of other ampersand-containing things
    text = re.sub(r'&#\d+;', '', text)
    for key, value in replacements.iteritems():
        text = text.replace(key, value)
    # Now remove all the other non-ascii chars if don't need unicode support
    if not uni:
        text = ''.join(c for c in text if 0 < ord(c) < 128)
    # Get rid of hashtags and mentions too
    text = re.sub(r'[@#]\w+[ ]*', '', text)

    # Get rid of punctuation 
    text = text.translate(None, string.punctuation)

    # Remove stopwords 
    text = preprocessors.filter_by_list(text, preprocessors.stopwordsfile_long)

    # Tabs?
    text = text.replace('\t', '')
    return text.strip(' ')



