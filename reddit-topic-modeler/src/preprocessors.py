"""
This module provides preprocessing functions on the document raw text level, i.e., just a
submission's text fields (title, text, and the submission's comment text fields), as one string. 
"""

import re
import os
import string
import stemmer

# Don't accept word lengths outside of these bounds
_max_word_length = 15
_min_word_length = 3

# Regex to match a url 
url = re.compile(r"(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?")

# Regex to match reference to other subreddit 
ref = re.compile(r"(\s|^)(/?r/)([\w]+)")

# Regex to match number 
numeric = re.compile(r"([0-9]+)")

# Eliminate symbolic links 
path = os.path.realpath(__file__).split('/')
jpath = '/'.join(path[:-1])

# Stopwords 
stopwordsfile = open(jpath + '/../data/stopwords/stopwords.txt').read().splitlines()
stopwordsfile_long = open(jpath + "/../data/stopwords/stopwords_long.txt").read().splitlines()

stopwords = map(lambda word: word.replace("'", ""), stopwordsfile)
stopwords_long = []
for stop in stopwordsfile_long:
	words = stop.split("\t")
	stopwords_long.extend(map(lambda word: word.replace("'", ""), words))


'''
Apply filters and functions. Facilitates adding more filters and functions. 
'''

# General method to apply a filter.
def applyFilter(function, text, wordlist=None): return ' '.join(filter(lambda word: function(word), text.split()))

# General method to apply a preprocessing function to a document. 
def applyFn(function, text): return ' '.join(map(lambda word: function(word), text.split()))


'''
Filters 
'''

# Common use would be to remove stopwords. 
def filter_by_list(text, wordlist):
	fn = lambda word: word not in wordlist
	return applyFilter(fn, text, wordlist=wordlist)

# Remove words that fall outside of word length bounds. 
def filter_by_length(text, min_length=_min_word_length, max_length=_max_word_length):
	fn = lambda word: len(list(word)) > min_length and len(list(word)) < max_length
	return applyFilter(fn, text)

'''
Functions 
'''

# Should extract websites and references to other subreddits first since this
# method will remove them. 
def clean(text):
	# Remove these specifics
	removals = ['&lt;', '&gt;', '&amp;', '[deleted]']
	for rem in removals:
		text = text.replace(rem, ' ')
	# Remove websites 
	text = re.sub(url, '', text)
	# Remove references to other subreddits 
	text = re.sub(ref, '', text)
	# Remove remaining punctuation 
	punctuation = '!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~'
	for char in punctuation:
		text = text.replace(char, ' ')
	# Punctuation special case: apostrophe
	text = text.replace("'", '')
	# Remove numeric characters
	for match in re.finditer(numeric, text):
		text = text.replace(match.groups()[0], '')
	# Remove extra whitespace
	text = ' '.join(text.split()).lower()
	return text
	
def remove_non_ascii(s):
	return filter(lambda x: x in string.printable, s)
 
# Stem each word in document. Best if clean has been called first. 
def stem(text): return applyFn(stemmer.stem, text)

# Extract website names from all links found in document. Should probably 
# be called before clean. 
def extract_websites(text):
	websites = []
	for match in re.finditer(url, text):
		name = match.groups()[1].replace('www.', '')
		# Ignore internal links 
		if name != 'reddit.com':
			websites.append(name)
	return websites

# Extract references to other subreddits.
def extract_references(text):
	references = []
	for match in re.finditer(ref, text):
		references.append(match.groups()[2])
	return references

# TO DO: Extracts relevant text from a bunch of html. 
def text_from_html(html): return html

