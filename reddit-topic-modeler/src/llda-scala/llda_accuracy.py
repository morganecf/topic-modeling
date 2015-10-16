"""
Script to compute accuracy of LLDA model on test set. Saves in database. 
"""

import sys
from redditDB import RedditDB

modelkey = sys.argv[1]

base_path = "../data/llda-cvb0-cee38496-3-dd7c685c-46a60775/01000"
topic_distrib_path = base_path + "llda_test_"+modelkey+"-document-topic-distributuions.csv"
labels_path = base_path + "label-index.txt"

labels = open(labels_path).read().splitlines()
f = open(topic_distrib_path).read().splitlines()

correct = 0

for line in f:
	parts = line.split(",")
	label = parts[0]	# Actual label
	distribution = map(lambda x: float(x), parts[1:])
	guess = distribution.index(max(distribution))
	if labels[guess] == label:
		correct += 1

# TODO: Compute false positives, negatives, etc. 

accuracy = float(correct)/float(len(f))
print "Accuracy:", str(accuracy*100), "%"

rdb = RedditDB()
result_doc = { "metadata_id":modelkey, "llda_accuracy": accuracy }
rdb.add_result(result_doc)


