"""
Creates an edge list of co-occurrences based on users submitting to or 
commenting on different subreddits. 

For example:
5   30   25 

where soccer = 5 and nfl = 30, means that 25 people have submitted to or
commented on the soccer and nfl subreddits.

For now, weight is sum of comments and submissions.  

For fast modularity community detection, cannot have self-loops or multi-edges 
and each file must contain a connected component.

TODO: How to weight comentions? if someone posts to soccer and nfl 10 times vs 1, right
now that counts as one when aggregating but should maybe be weighted more?  

Usage: python subreddit_edges.py <limit> <output>
"""

import redditDB as rdb
import sys
import math 

# To count as an edge must be greater than this threshold 
WEIGHT_THRESH = 2

# Returns a connected component 
def BFS(graph, subreddits):
	found = []
	first = subreddits.keys()[0]
	queue = [first]
	while len(queue) > 0:
		next = queue.pop()
		if next in subreddits:
			del subreddits[next]
			# Go through each neighbor 
			for k, v in graph[next].iteritems():
				# Normalized by subreddit's total activity 
				vn = float(v) / float(sum(graph[next].values()))
				# Log-normalized
				vl = math.log(v)
				found.append((next, k, v, vn, vl))
				queue.append(k)	
	return found

# Get number of users to look at 
limit = int(sys.argv[1])

# Get dir where edges will be stored 
directory = sys.argv[2] 
if not directory.endswith("/"):
	directory = directory + "/"

# Get users 
r = rdb.RedditDB("mciot", sys.argv[3], "blacksun.cs.mcgill.ca", 31050, "reddit_topics")
users = r.get_users()


# Form: {topic1: {topicA: 40, topicB: 20, topicC:2}}
graph = {}

# key will contain an integer for each subreddit 
sid = 0
key = {}

# Get a user's posting information 
for user in users:

	# If limit was negative number, will never go to 
	# 0 so will use all users 
	limit -= 1
	if limit == 0:
		break

	submissions = user.get(u"submissions") or {}
	comments = user.get(u"comments") or {}

	# First correct for $ - mongodb mistake
	if "$" in submissions:
		dollar = submissions["$"]
		for k, v in dollar.iteritems():
			try:
				submissions[k] += v
			except KeyError:
				submissions[k] = v 
		del submissions["$"]
	if "$" in comments:
		dollar = comments["$"]
		for k, v in dollar.iteritems():
			try:
				comments[k] += v
			except KeyError:
				comments[k] = v 
		del comments["$"]

	subreddits = list(set(submissions.keys() + comments.keys()))

	if len(subreddits) == 1:
		graph[subreddits[0]] = {}
		continue

	for s1 in subreddits:

		# Update key 
		if s1 not in key:
			key[s1] = sid 
			sid += 1

		for s2 in subreddits:
			if s1 != s2: 

				# Update graph 
				try:
					k = graph[s1]
					try:
						graph[s1][s2] += 1
					except KeyError:
						graph[s1][s2] = 1
				except KeyError:	
					graph[s1] = {s2 : 1}


print "Done creating graph."
print "Num nodes:", len(graph)
print "Finding connected components."

# Find connected components 
components = []
subreddits = dict(key)
while len(subreddits) > 0:
	found = BFS(graph, subreddits)
	components.append(found)

print "Found", len(components), "components"

# decimal-norm: normalized by total subreddit activity
# integer-norm: normalized by total subreddit activity and rounded to int
# decimal-log: log-normalized
# integer-log: log-normalized and rounded to int
# unweighted: no weights
# integer: raw integer weights

# Save connected components (with and without weights)
for i, component in enumerate(components):
	
	# Open files corresponding to different kinds of weighting schemes 
	f = open(directory + "unweighted/component" + str(i) + ".pairs", "w")
	fc = open(directory + "integer/component" + str(i) + ".wpairs", "w")
	fdn = open(directory + "decimal-norm/component" + str(i) + ".wpairs", "w")
	fdl = open(directory + "decimal-log/component" + str(i) + ".wpairs", "w")
	fin = open(directory + "integer-norm/component" + str(i) + ".wpairs", "w")
	fil = open(directory + "integer-log/component" + str(i) + ".wpairs", "w")

	for quintuple in component:
		# Subreddits 
		s1 = str(key[quintuple[0]])
		s2 = str(key[quintuple[1]])
		# Regular count 
		count = str(quintuple[2])
		# Normalized count 
		norm = str(quintuple[3])
		# Log-normalized count 
		log = str(quintuple[4])
		# Rounded normalized and log-normalized counts
		norm_round = str(math.ceil(quintuple[3]))
		log_round = str(math.ceil(quintuple[4]))

		# Write to individual files 
		f.write(s1 + "\t" + s2 + "\n")
		fc.write(s1 + "\t" + s2 + "\t" + count + "\n")
		fdn.write(s1 + "\t" + s2 + "\t" + norm + "\n")
		fdl.write(s1 + "\t" + s2 + "\t" + log + "\n")
		fin.write(s1 + "\t" + s2 + "\t" + norm_round + "\n")
		fil.write(s1 + "\t" + s2 + "\t" + log_round + "\n")

	f.close()
	fc.close()
	fdn.close()
	fdl.close()
	fin.close()
	fil.close()

# Save key 
f = open(directory + "key.txt", "w")
for k, v in key.iteritems():
	f.write(k + "\t" + str(v) + "\n")
f.close()



