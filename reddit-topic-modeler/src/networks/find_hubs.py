"""
Collects degree information from network. Saves the degree
distribution of the network and prints out potential hubs
(those with degree greater than or equal to input degree threshold
and within a cluster of size greater than some input threshold.)
For now have hardcoded thresholds.

Usage: python find_hubs.py <network> <clusters>
"""

import sys
import networkx as nx

network_file = sys.argv[1]
cluster_file = sys.argv[2]
# degree_threshold = sys.argv[3]
# cluster_size_threshold = sys.argv[4]

degree_threshold = 80
cluster_size_threshold = 100

edges = open(network_file).read().splitlines()
lines = open(cluster_file).read().splitlines()

# Indexed by subreddit, and shows size of cluster it belongs to
clusters = {}

for i in range(len(lines)):
	line = lines[i]
	if line.startswith("GROUP"):
		i += 1
		group = []
		while i < len(lines) and not lines[i].startswith("GROUP"):
			group.append(lines[i])
			i += 1
		for member in group:
			clusters[member] = len(group)

# Build graph
graph = nx.Graph()

for edge in edges:
	try:
		s1, s2, weight = edge.split('\t')
		graph.add_edge(s1, s2, weight=float(weight))
	except ValueError:
		print "Bad line?", edge
		continue

nodes = graph.nodes()

# Cluster by degree
degrees = {}
for node in nodes:
	degree = graph.degree(node)
	try:
		degrees[degree].append(node)
	except KeyError:
		degrees[degree] = [node]

# Cluster by subreddit
degrees_by_subeddit = {}
for node in nodes:
	degree = graph.degree(node)
	degrees_by_subeddit[node] = degree

# Get degree stats
tuples = map(lambda k: (k, len(degrees[k])), degrees.keys())		# [(degree, count)...]
by_degree = sorted(tuples, reverse=True)
by_count = sorted(tuples, key=lambda t: t[1], reverse=True)

# Save distribution and hubs
if cluster_file.endswith('/'):
	cluster_file = cluster_file[:-1]
name = cluster_file.split('/')[-1].split('.')[0]

print name
print cluster_file

path = '/'.join(cluster_file.split('/')[:-1])
print path
degree_out = open(path + '/analysis/degree_distribution_' + name + '.txt', 'w')
subreddits_out = open(path + '/analysis/subreddits_by_degree_' + name + '.txt', 'w')
hub_out = open(path + '/analysis/hubs_' + name + '.txt', 'w')
cluster_out = open(path + '/analysis/subreddits_by_cluster_size_' + name + '.txt', 'w')

# Print distribution
print "Degree distribution:"
print "degree\tcount"
degree_out.write("Degree\tCount\n")
for degree, count in by_count:
	subreddits = ','.join(degrees[degree])
	print degree, '\t', count
	degree_out.write(str(degree) + '\t' + str(count) + '\n')

degree_out.close()

print "\nPotential hubs (d >= 100):"
hub_out.write("Degree\tCluster size\tSubreddit\n")
subreddits_out.write("Subreddit\tDegree\tCluster size\n")
for degree, count in by_degree:
	subreddits = degrees[degree]
	if degree >= degree_threshold:
		print "Degree:", degree
		for subreddit in subreddits:
			cluster_size = clusters[subreddit]
			print "\t", subreddit, '\t', cluster_size

			subreddits_out.write(subreddit + '\t' + str(degree) + '\t' + str(cluster_size) + '\n')

			if cluster_size > cluster_size_threshold:
				hub_out.write(str(degree) + '\t' + str(cluster_size) + '\t' + subreddit + '\n')

hub_out.close()
subreddits_out.close()

# Find the highest-degree nodes in largest clusters
clusters_by_size = {}
for sr, size in clusters.iteritems():
	try:
		clusters_by_size[size].append(sr)
	except KeyError:
		clusters_by_size[size] = [sr]

cluster_tuples = sorted(list(clusters_by_size.iteritems()), reverse=True)
for size, subreddits in cluster_tuples:
	if size > cluster_size_threshold:
		sr_degrees = {}
		for subreddit in subreddits:
			degree = degrees_by_subeddit[subreddit]
			try:
				sr_degrees[degree].append(subreddit)
			except KeyError:
				sr_degrees[degree] = [subreddit]

		print 'Cluster size:', size
		cluster_out.write("Cluster size: " + str(size) + '\n')
		sorted_degrees = sorted(list(sr_degrees.iteritems()), reverse=True)
		for deg, subreddits in sorted_degrees:
			if deg > degree_threshold:
				subreddit_str = ','.join(subreddits)
				print '\tDegree:', deg, '\t', subreddit_str
				cluster_out.write("\tDegree: " + str(deg) + '\t' + subreddit_str + '\n')

cluster_out.close()