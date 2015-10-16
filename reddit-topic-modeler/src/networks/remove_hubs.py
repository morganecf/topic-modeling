"""
Takes a network file and list of hubs and removes the hubs from the
network. Assumes hub file was generated by find_hubs and has form
cluster size: <int>
	degree: <int> \t subreddit1,subreddit2,....subredditn
usually called subreddits_by_cluster.txt

Usage: python remove_hubs.py <network> <hubs> <out>
"""

import sys

edges = open(sys.argv[1]).read().splitlines()
hub_lines = open(sys.argv[2]).read().splitlines()
out = open(sys.argv[3], 'w')

hubs = {}
for line in hub_lines:
	if line.startswith('\tDegree:'):
		sr = line.split('\t')[2].strip()
		hubs[sr] = 1

removed = 0

for edge in edges:
	try:
		s1, s2, weight = edge.split('\t')
	except ValueError:
		print 'bad line:', edge
		continue
	if not (s1 in hubs or s2 in hubs):
		out.write(edge + '\n')
		removed += 1

out.close()

print removed, "edges removed"

