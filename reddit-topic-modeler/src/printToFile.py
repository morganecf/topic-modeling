"""
Script to output Reddit text and labels to a 
csv file based on conf file parameters. 
"""

import sys

import preprocess
import utils
from conf import Conf

# TODO: Have more sophisticated argument parser
conf_file = sys.argv[1]

# Create conf object. Can now access params, including db connection 
params = Conf(conf_file)

# If topics weren't specified use all the topics 
# Each document should be one line (submission + comments)
if not params.topics:
	topics = params.db.subreddit_list()
else:
	topics = params.topics

# Get the documents in Reddit format 
print "Retrieving documents..."
reddit_documents = preprocess.getData(topics, params.comment_level, params.num_docs, params.db)
print reddit_documents
# Preprocess these 
print "Preprocessing documents..."
preprocess.preprocess(reddit_documents, params.max_word_length, params.min_word_length, params.stopwords, params.stem)
print reddit_documents
''' TODO: removal_threshold and removal_perc '''

# Split into train and test 
print "Splitting into train and test sets..."
train,test = utils.partition(reddit_documents, .9)

# Now save metadata to db to remember parameter configuration
print "Saving metadata to mongodb..."
metadata = utils.createMetaData(params)
result = params.db.add_metadata(metadata)
if result:
	print "Save successful."
else:
	print "Save not successful."

# Print each document to file
# Add metadata's db id to filename to be able to match up to metadata in db
#timestamp = '_'.join(str(datetime.today()).split())
trainpath = "../data/scala/llda_train_"+str(result)+".csv"
testpath = "../data/scala/llda_test_"+str(result)+".csv"
ftrain = open(trainpath, "wt")
ftest = open(testpath, "wt")

print "Saving training set to", trainpath
print "Saving test set to", testpath
print "Metadata id:", result
for document in train:
	string = document.topic + "," + " ".join(document.words) + "\n" 
	ftrain.write(string.encode("utf8"))

for document in test:
	string = document.topic + "," + " ".join(document.words) + "\n"
	ftest.write(string.encode("utf8"))

ftrain.close()
ftest.close()





