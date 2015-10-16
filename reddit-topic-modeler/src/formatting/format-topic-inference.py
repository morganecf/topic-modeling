""" 
This script breaks up a formatted HDP/LDA/SLDA input 
file into a training and test set. 

Usage: python format-topic-inference.py <matrix.txt> <labels.txt> <perc> <results>,
where perc specifies the percentage of documents to leave out for each topic in the training set, 
and results is the path to the directory where you want all the results to be stored. 
""" 

import sys
import random
from itertools import izip

# Get arguments 
try:
	dataf = sys.argv[1]
	labelsf = sys.argv[2]
	results = sys.argv[4]
	try:
		perc = float(sys.argv[3])
		if perc >= 1:
			raise ValueError
	except ValueError:
		"Arg <perc> should be a number between 0 and 1, exclusive."
		raise IndexError
except IndexError:
	print "Usage: python format-topic-inference.py <matrix.txt> <labels.txt> <label-key.txt> <perc>"
	sys.exit(1)

# Training set 
trainf = open(results + "/train.txt", "w")
trainlabelsf = open(results + "/train_labels.txt", "w")

# Test set 
testf = open(results + "/test.txt", "w")
testlabelsf = open(results + "/test_labels.txt", "w")

# Go through data one line at a time 
with open(dataf) as data, open(labelsf) as labels:
	for line, label in izip(data, labels):
		# Add it to test set with certain probability
		r = random.random()
		if r <= perc:
			testf.write(line)
			testlabelsf.write(label)
		else:
			trainf.write(line)
			trainlabelsf.write(label)

trainf.close()
testf.close()
trainlabelsf.close()
testlabelsf.close()










