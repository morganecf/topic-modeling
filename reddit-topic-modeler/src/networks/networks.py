'''
Generate connected components of subreddit networks for use
in clustering algorithms. Also outputs index>subreddit mapping file.

Usage: python connected_components.py <network tsv file> <results_dir> <directed/undirected> <threshold>
Ex: python connected_components.py ../data/networks/final_xpost_network.tsv ./data/networks/xpost/final-directed-1 1

Will omit any edges with weight less than or EQUAL to <threshold>.
If omit the threshold argument or use int < 0, uses all edges.

xpost - directed?
related - directed

user - undirected
subdomain - undirected
'''

import os
import sys
import networkx as nx
from operator import itemgetter

# BFS if connected components taking too long
# def BFS():
# 	print "Getting highest-degree node..."
# 	start_node = sorted(graph.degree_iter(), key=itemgetter(1), reverse=True)[0]
# 	print start_node[0], start_node[1]
#
# 	print "Finding 'largest' component.."
# 	component = list(nx.bfs_edges(graph, start_node[0]))
# 	print len(component), "edges"
#
# 	print "Saving..."
#
# 	path = fpath.replace('.tsv', '_BFS')
# 	os.system('mkdir ' + path)
#
# 	f = open(os.path.join(path, 'component.wpairs'), 'w')
# 	fn = open(os.path.join(path, 'component_norm.wpairs'), 'w')
# 	fi = open(os.path.join(path, 'component_int.wpairs'), 'w')
# 	fin = open(os.path.join(path, 'component_int_norm.wpairs'), 'w')
#
# 	for node1, node2 in component:
# 		node1_id = mapping[node1]
# 		node2_id = mapping[node2]
#
# 		weight = graph[node1][node2]['weight']
# 		total_weight = sum(map(lambda v: v['weight'], graph[node1].values()))
# 		norm_weight = weight / float(total_weight)
#
# 		f.write(str(node1_id) + '\t' + str(node2_id) + '\t' + str(weight) + '\n')
# 		fn.write(str(node1_id) + '\t' + str(node2_id) + '\t' + str(norm_weight) + '\n')
# 		fi.write(str(node1_id) + '\t' + str(node2_id) + '\t' + str(int(weight)) + '\n')
# 		fin.write(str(node1_id) + '\t' + str(node2_id) + '\t' + str(int(norm_weight)) + '\n')
#
# 	f.close()
# 	fn.close()
# 	fi.close()
# 	fin.close()


# Load file containing edge list
fpath = sys.argv[1]
out = sys.argv[2]
network_type = sys.argv[3]
directed = False
if network_type == 'directed':
	directed = True

print "Loading raw edges..."
edges = open(fpath).read().splitlines()

# Get threshold
try:
	threshold = int(sys.argv[4])
except IndexError:
	threshold = -1

graph = nx.Graph()

print "Initializing total network:", len(edges), "edges\n"

# Will contain nodes not contained in a single edge
# after thresholding
singletons = set()

for line in edges:
	try:
		node1, node2, weight = line.split('\t')
	except ValueError:
		try:
			node1, node2 = line.split('\t')
			weight = 1
		except ValueError:
			continue
	singletons.add(node1)
	singletons.add(node2)
	if node1 != node2:
		w = float(weight)
		if w <= threshold:
			continue
		graph.add_edge(node1, node2, weight=float(weight))
		singletons.remove(node1)
		singletons.remove(node2)

print len(graph.nodes()), "nodes"
print len(graph.edges()), "edges"
print len(singletons), "singletons\n"
print "Finding connected components..."

components = nx.connected_component_subgraphs(graph)

# Create results directories for connected components with
# regular and normalized edge weights in both decimal and int format
delim = ' ' + os.path.join(out, '')

# Can only normalize edge weights in directed graphs
if directed:
	dirs = delim.join(['', 'regular', 'regular-int', 'normalized', 'normalized-int'])
else:
	dirs = delim.join(['', 'regular', 'regular-int'])

os.system('mkdir ' + out)
os.system('mkdir' + dirs)

# Create directory that will store subreddit to id mappings
mapping_dir = os.path.join(out, 'mappings')
os.system('mkdir ' + mapping_dir)

print "Writing connected components to file..."

weight_distribution = {}
component_distribution = {}

i = 0
weight_total = 0
weight_norm_total = 0
for component in components:

	# Will contain subreddit to numerical id mapping
	mapping = {}

	# Start numerical ids at 0
	id_counter = -1

	fname = 'component' + str(i) + '.wpairs'

	f = open(os.path.join(out, 'regular', fname), 'w')
	fi = open(os.path.join(out, 'regular-int', fname), 'w')
	if directed:
		fn = open(os.path.join(out, 'normalized', fname), 'w')
		fin = open(os.path.join(out, 'normalized-int', fname), 'w')

	num_edges = 0
	for edge in component.edges(data=True):
		num_edges += 1

		if edge[0] not in mapping:
			id_counter += 1
			mapping[edge[0]] = id_counter
		if edge[1] not in mapping:
			id_counter += 1
			mapping[edge[1]] = id_counter

		node = mapping[edge[0]]
		neighbor = mapping[edge[1]]
		weight = edge[2]['weight']

		f.write(str(node) + '\t' + str(neighbor) + '\t' + str(weight) + '\n')
		fi.write(str(node) + '\t' + str(neighbor) + '\t' + str(int(weight)) + '\n')
		if directed:
			total_weight = sum(map(lambda data: data['weight'], graph.adj[edge[0]].values()))
			norm_weight = weight / float(total_weight)
			weight_norm_total += norm_weight
			fn.write(str(node) + '\t' + str(neighbor) + '\t' + str(norm_weight) + '\n')
			fin.write(str(node) + '\t' + str(neighbor) + '\t' + str(int(norm_weight)) + '\n')

		weight_total += weight
		try:
			weight_distribution[int(weight)] += 1
		except KeyError:
			weight_distribution[int(weight)] = 1

	print 'Component', i, ':', num_edges, 'edges'
	try:
		component_distribution[num_edges] += 1
	except KeyError:
		component_distribution[num_edges] = 1

	f.close()
	fi.close()
	if directed:
		fn.close()
		fin.close()

	# Save individual mappings
	mapname = 'mapping' + str(i) + '.txt'
	mapping_output = open(os.path.join(mapping_dir, mapname), 'w')
	for sr, nid in mapping.iteritems():
		mapping_output.write(str(nid) + '\t' + sr + '\n')
	mapping_output.close()

	i += 1

print "Saving degree distribution..."
nodes_by_degree = []
for node in graph.nodes():
	degree = graph.degree(node)
	nodes_by_degree.append((degree, node))

nodes_by_degree.sort(reverse=True)

degree_out = open(os.path.join(out, 'degree_distribution.txt'), 'w')
for degree, node in nodes_by_degree:
	degree_out.write(str(degree) + '\t' + node + '\n')
degree_out.close()

print "Saving network stats..."

# Save singletons
if len(singletons) > 0:
	single = open(os.path.join(out, 'singletons.txt'), 'w')
	for singleton in singletons:
		single.write(singleton + '\n')
	single.close()

# Save information about network
density = len(graph.edges()) / float(len(graph.nodes()) * (len(graph.nodes()) - 1))

total_num_edges = len(graph.edges())

info = open(os.path.join(out, 'info.txt'), 'w')
info.write('Input network: ' + fpath + '\n')
info.write('Threshold: ' + str(threshold) + '\n')
info.write('Directed: ' + str(directed) + '\n')
info.write('Original number of edges: ' + str(len(edges)) + '\n')
info.write('Number of nodes (unique subeddits): ' + str(len(graph.nodes())) + '\n')
info.write('Number of singletons (subreddits not connected to any other after thresholding): ' + str(len(singletons)) + '\n')
info.write('Density (undirected): ' + str(2 * density) + '\n')
info.write('Density (directed): ' + str(density) + '\n')
info.write('Number of edges in graph after thresholding: ' + str(total_num_edges) + '\n')
info.write('Average edge weight: ' + str(weight_total / float(total_num_edges)) + '\n')
if directed:
	info.write('Average normalized edge weight: ' + str(weight_norm_total / float(total_num_edges)) + '\n')
info.write('Edge weight distribution: (weight, num edges with this weight, %)' + '\n')
for weight, val in weight_distribution.iteritems():
	info.write('\t' + str(weight) + '\t' + str(val) + '\t' + str((val / float(total_num_edges)) * 100) + '\n')
info.write('Number of connected components: ' + str(i) + '\n')
info.write('Connected component edge distribution: (number of edges, number of CC with this number of edges, %)' + '\n')
for edge_num, val in component_distribution.iteritems():
	info.write('\t' + str(edge_num) + '\t' + str(val) + '\t' + str((val / float(total_num_edges)) * 100) + '\n')
info.close()

print "\nDone!\n\n"
os.system('cat ' + os.path.join(out, 'info.txt'))