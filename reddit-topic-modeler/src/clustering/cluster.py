"""
Takes a file of dumped reddit data and the result of elucidate_clusters.py 
to produce two files:

1. Essentially the same file but with new subreddit
labels corresponding to the clusters original subreddits
belong to.

## WELL not producing this one yet 
2. A file where each cluster gets its own line...this might not be a good idea? 

Usage: python cluster.py <dump_file> <clusters> <outputdir>
"""

import sys

dumpf = sys.argv[1]
clusterf = sys.argv[2]
outputd = sys.argv[3]
if not outputd.endswith("/"):
	outputd = outputd + "/"

# Create clusters 
label = 0
info = open(clusterf).read().splitlines()
clusters = {}
for i in range(len(info)):
	line = info[i]
	if line.startswith("GROUP"):
		i += 1
		groupname = "".join(line.split())
		while i < len(info) and not info[i].startswith("GROUP"):
			sr = info[i]
			clusters[sr] = str(label)
			i += 1
		label += 1 


# Create name of output file path. Will be composed of
# given path plus dump file name plus cluster file name. 
#clustering/nov_1000/groups.txt/
if dumpf.endswith("/"):
	dumpname = dumpf.split("/")[-2].replace(".txt", "")
else:
	dumpname = dumpf.split("/")[-1].replace(".txt", "")

if clusterf.endswith("/"):
	clustername = clusterf.split("/")[-3] + "-" + clusterf.split("/")[-2]
else:
	clustername = clusterf.split("/")[-2] + "-" + clusterf.split("/")[-1]

outputf = outputd + dumpname + "-" + clustername
wf = open(outputf, "w")

# Go through dump file and find which cluster each line belongs to 
found = 0
notfound = 0
with open(dumpf, "r") as f:
	for line in f:
		info = line.split(",")
		sr = info[0].strip()
		try:
			group = clusters[sr]
			found += 1
		except KeyError:
			notfound += 1
			continue
		replacement = group + "," + ",".join(info[1:]) + "\n"
		wf.write(replacement)

wf.close()
print "num found:", found
print "num not found:", notfound


