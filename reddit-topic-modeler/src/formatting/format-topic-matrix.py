"""
Formats data into frequency matrix 
that can be given to David Blei's
LDA-C, HDP-C, and SLDA-C++ implementations. 

Takes three parameters: the data (all the text),
the unique sorted word list, and name of directory
where everything will be stored. Saves sparse 
vector representation of each document on a separate 
line. Also saves estimated alpha and label lists 
to separate files. 

Use --help to see other optional parameters. 

Format of each line should be:
M  term_1:count  term_2:count ... term_n:count

Where M is the number of unique words in the 
document, terms are indexes from the unique
word list, and count is the number of time 
the term appears in the document. 
"""

import argparse
from collections import defaultdict 

argparser = argparse.ArgumentParser(description="Format reddit data into LDA/SLDA/HDP-compatible input")
argparser.add_argument("--data", help="path to dumped data", required=True)
argparser.add_argument("--words", help="path to unique word list", required=True)
argparser.add_argument("--layer", help="only use comments up to and including layer <layer>", default=3)
argparser.add_argument("--topics_file", help="path to topics file - use if only want to model certain topics", default=None)
argparser.add_argument("--output", help="path to output directory", required=True)

# TODO: Could have arguments for choosing random number of topics or documents 
# or documents per topic 

# This is kind of bad since argparser isn't supposed to be used for flags,
# just arguments :/
argparser.add_argument("--links", help="use true to use link content", default=False)

params = argparser.parse_args()

# Required
datafile = params.data
wordfile = params.words
outputdir = params.output

# Optional 
topicsfile = params.topics_file
layer = int(params.layer)
links = True if params.links == "true" else False 

# First read in unique words
unique = open(wordfile).read().splitlines()

# Now index words for easy O(1) searching 
words = {}
for i,w in enumerate(unique):
	words[w] = i

# Index topics if topics file is specified
topics = {}
if topicsfile:
	tf = open(topicsfile).read().splitlines()
	for i,t in enumerate(tf):
		topics[t] = i

# Keep track of number of topics 
numlabels = 0
labels = {}

# Will keep track of average number of used words per document 
# which is used to approximate alpha (for LDA)
total = 0
num_docs = 0

# Will save matrix in this file 
mf = open(outputdir + "/matrix.txt", "w")
# Will save list of labels in this file 
lf = open(outputdir + "/labels.txt", "w")

# Process data line by line 
with open(datafile) as f:
	for line in f:

		line = line.split(",")

		# Line should have at least 3 commas 
		if len(line) < 3:
			continue

		topic = line[0]

		# If a topicsfile was specified, 
		# see if topic is in it. If so,
		# use its index as the label #. 
		if topicsfile:
			try:
				label = topics[topic]
			except KeyError:
				# Ignore documents not in topics file
				continue
		else:
			try:
				# Topic already exists 
				label = labels[topic]
			except KeyError:
				# Found a new topic 
				labels[topic] = numlabels
				label = numlabels
				numlabels += 1

		# Submission content 
		text = line[1] 

		# Add link content if specified 
		if links:
			text += line[2]

		# Add comments up to and including specified layer, or all (if -1)
		comments = line[2:]
		if layer < 0:
			maxlayer = len(comments)
		else:
			maxlayer = min(layer + 1, len(comments))
		text += " ".join(comments[:maxlayer])

		d = defaultdict(int)
		for word in text.split():
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

		# Don't bother with any documents that 
		# have no terms. 
		if M > 0:
			mf.write(str(M) + " " + formatted + "\n")
			lf.write(str(label) + "\n")
mf.close()
lf.close()

# Save label key 
lkf = open(outputdir + "/label-key.txt", "w")
if topicsfile:
	for topic,label in topics.iteritems():
		lkf.write(topic + "\t" + str(label) + "\n")
else:
	for topic,label in labels.iteritems():
		lkf.write(topic + "\t" + str(label) + "\n")
lkf.close()

# Save approximation of alpha (for LDA) to a file 
avg = float(total) / float(num_docs)
alpha = str(float(avg) / float(len(words)))
afp = open(outputdir + "/alpha.txt", "w")
afp.write(alpha)
afp.close()