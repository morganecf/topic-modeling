"""
Creates an edge list of co-occurrences based on users submitting to or 
commenting on different subreddits. 

For example:
soccer   nfl   25 

means that 25 people have submitted to or commented on the soccer and nfl subreddits. 
"""

import json
import redditDB as rdb

r = rdb.RedditDB("mciot", "r3dd1tmorgane", "blacksun.cs.mcgill.ca", 31050, "reddit_topics")

users = r.get_users()

def combinations(l):
	combos = []
	for item1 in l:
		for item2 in l:
			if item1 != item2:
				combos.append((item1, item2))
	return combos

# Form: {(topic1, topic2):15}
# For now, tally comments and submissions
# equally 
graph = {}

# How to weight comentions? 
# soccer-50, football-50, cooking-2 (from same person)

submission_nodes = {}
comment_nodes = {}

limit = 10

for user in users:
	# Small number of users for now 
	limit -= 1
	if limit == 0:
		break

	try:
		submissions = combinations(user[u"submissions"].keys())
		comments = combinations(user[u"comments"].keys())
		
		for sub in submissions:
			try:
				graph[sub] += 1
			except KeyError:
				reverse = (sub[1], sub[0])
				try:
					graph[reverse] += 1
				except KeyError:
					graph[sub] = 1

			try: 
				submission_nodes[sub[0]] += 1
			except KeyError:
				submission_nodes[sub[0]] = 1
			try:
				submission_nodes[sub[1]] += 1
			except KeyError:
				submission_nodes[sub[1]] = 1

		for comm in comments:
			try:
				graph[comm] += 1
			except KeyError:
				reverse = (comm[1], comm[0])
				try:
					graph[reverse] += 1
				except KeyError:
					graph[comm] = 1

			try: 
				comment_nodes[comm[0]] += 1
			except KeyError:
				comment_nodes[comm[0]] = 1
			try:
				comment_nodes[comm[1]] += 1
			except KeyError:
				comment_nodes[comm[1]] = 1

	except KeyError:
		pass

total = list(set(comment_nodes.keys() + submission_nodes.keys()))
json_total = map(lambda t: {"name" : t}, total)

# json_obj = {"nodes": {"comments": json_comments, "submissions": json_submissions}, "links": []}
json_obj = {"nodes": json_total, "links": []}

for k,v in graph.iteritems():
	src = total.index(k[0])
	trg = total.index(k[1])
	if v > 2:
		json_obj["links"].append({"source":src, "target":trg, "weight":v})

print len(json_obj["nodes"]), "subreddits"
print len(json_obj["links"]), "connections"

json.dump(json_obj, open("../data/smalleredgelist.json", "w"))
