"""
Formats data into frequency matrix 
that can be given to David Blei's
C LDA implementation. Takes two
parameters: the data (all the text)
and the unique sorted word list. Prints out
sparse vector representation of each
document on a separate line. 

Format of each line should be:
M  term_1:count  term_2:count ... term_n:count

Where M is the number of unique words in the 
document, terms are indexes from the unique
word list, and count is the number of time 
the term appears in the document. 
"""

import sys
from collections import defaultdict 

try:
	datafile = sys.argv[1]
	wordfile = sys.argv[2]
	thresh = sys.argv[3]
except IndexError:
	print "Usage: python format-lda-c.py <path to data> <path to unique sorted word count list> <threshold>"
	sys.exit(1)


# First read in unique words (should be sorted with counts)
unique = open(wordfile).read().splitlines()

# Now index words and remove words below certain threshold count
words = {}
for i,w in enumerate(unique):
	# count, word
	info = w.split()
	if int(info[0]) <= 5:
		words[info[1]] = i

# Will keep track of average number of used words per document 
# which is used to approximate alpha (for LDA)
total = 0
num_docs = 0

# Then process data line by line 
with open(datafile) as f:
	for line in f:

		d = defaultdict(int)
		for word in line.split():
			d[word] += 1

		formatted = ""
		M = len(d)
		for k,v in d.iteritems():
			try:
				i = words[k]
				formatted += " " + str(i) + ":" + str(v)
			# If word isn't found, was removed
			except KeyError:
				M -= 1

		total += M
		num_docs += 1

		print str(M) + " " + formatted


# Save approximation of alpha (for LDA) to a file 
avg = float(total) / float(num_docs)
alpha = str(float(avg) / float(len(words)))
afp = open("../../../data/unsupervised-LDA/alpha.txt", "w")
afp.write(alpha)
afp.close()