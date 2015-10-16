"""
Script to format user tweets to a text file 
that is compatible for inference using LDA,
SLDA, HDP, and Naive Bayes. 
"""

import argparse
from collections import defaultdict
from itertools import izip 

argparser = argparse.ArgumentParser(description="Format twitter data into LDA/SLDA/HDP/Naive Bayes-compatible input. Used for inference.")
argparser.add_argument("--tweets", help="path to tweet file", required=True)
argparser.add_argument("--ids", help="path to user id file", required=True)
argparser.add_argument("--words", help="path to unique word file", required=True)
argparser.add_argument("--dir", help="path to output directory", required=True)
params = argparser.parse_args()

tweetfile = params.tweets
idfile = params.ids
outputd = params.dir

# Put words into dict for O(1) access
words = {}
with open(params.words) as wf:
    index = 0
    for line in wf: 
        words[line.strip()] = index
        index += 1

print len(words), "words"

# Resulting information - name file in same way as original  
tfname = tweetfile.split("/")[-1].replace(".csv", ".txt")
ufname = idfile.split("/")[-1]
documents = open(outputd + "/" + tfname, "wt")  # For documents (tweets)
userids = open(outputd + "/" + ufname, "wt")

with open(tweetfile) as tweets, open(idfile) as ids:
    for line, userid in izip(tweets, ids):

        # First line is always None? AHRRRRGHHHHHHHHH
        #text = " ".join(line.split(",")[1:])
        text = line

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

        if M > 0:
            documents.write(str(M) + " " + formatted + "\n")
            userids.write(userid)

documents.close()
userids.close()

        

