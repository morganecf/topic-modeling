# quick script to convert text tweets/userids to csv file 
# for use in topical training 

import os
from utils import clean 

path = "../tweets-by-user/"

tweets = open("tweets.csv", "w")
ids = open("ids.csv", "w")

counter = 0

for f in os.listdir(path):
	counter += 1
	if counter % 100 == 0:
		print counter
	fname = os.path.join(path, f)
	uid = f.split("-")[2].split(".")[0]
	if os.path.isfile(fname):
		with open(fname, "r") as info:
			tweetstr = ""
			for index, line in enumerate(info):
				info = line.split("\t")
				tweetstr += info[-1].strip().replace("\n", "") + " "
		tweets.write(clean(tweetstr, False) + "\n")
		ids.write(uid + "\n")

tweets.close()
ids.close()
