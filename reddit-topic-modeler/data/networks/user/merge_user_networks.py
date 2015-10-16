"""
Merge user networks. Report on node degrees/potential hubs. 

Usage: python merge_user_networks.py <network file1> <network fil2> <combined network output file> 
Also saves nodes/their degrees in descending order in file with same name as output + _node_degrees.tsv 
"""

import sys 
import networkx as nx 

def addEdge(line, g):
	try:
		s1, s2, weight = line.split('\t')
		if g.has_edge(s1, s2):
			g[s1][s2]['weight'] += float(weight)
		elif g.has_edge(s2, s1):
			g[s2][s1]['weight'] += float(weight)
		else:
			g.add_edge(s1, s2, weight=float(weight))
	except ValueError:
		print 'bad line:', line  

def merge(f1, f2, out):
	g = nx.Graph()

	print "Loading file1...."
	with open(f1) as f:
		for line in f:
			line = line.strip()
			addEdge(line, g)

	print "Merging file2...."
	with open(f2) as f:
		for line in f:
			line = line.strip()
			addEdge(line, g)

	print "Saving total network..."
	output = open(out, 'w')
	for edge in g.edges(data=True):
		output.write(edge[0] + '\t' + edge[1] + '\t' + str(edge[2]['weight']) + '\n')
	output.close()

	print "Getting degree information..."
	nodes_by_degree = []
	for node in g.nodes():
		degree = g.degree(node)
		nodes_by_degree.append((degree, node))

	print "Sorting degree information..."
	nodes_by_degree.sort(reverse=True)

	print "Saving degree information..."
	degree_out = open(out.replace(".tsv", "_node_degrees.tsv"), 'w')
	for degree, node in nodes_by_degree:
		degree_out.write(str(degree) + '\t' + node + '\n')
	degree_out.close()

merge(sys.argv[1], sys.argv[2], sys.argv[3])

