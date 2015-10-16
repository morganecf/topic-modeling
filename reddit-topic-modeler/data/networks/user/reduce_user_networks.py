"""
Reduce user networks based on hubs. I.e., remove any
edges that contain a hub node. 
"""

info = open("final-user-networks/hubs-removed/info.txt", "w")

def reduce_network(fname, dname, limit):
	print fname 
	print "Getting degree information..."
	degree_info = open(dname).read().splitlines()[:limit]
	to_remove = set()
	for line in degree_info:
		degree, sr = line.split("\t")
		to_remove.add(sr.strip())

	print "Loading network edges..."
	edges = open(fname).read().splitlines()

	new_name = fname.replace(".tsv", "_h" + str(limit)) + ".tsv"
	new_path = new_name.split('/')[0] + '/hubs-removed/' + new_name.split('/')[1]
	reduced = open(new_path, 'w')

	print "Removing top", limit, "hubs and saving reduced network..."
	nodes = set()
	num_new_edges = 0
	for edge in edges:
		sr1, sr2, weight = edge.split("\t")
		sr1 = sr1.strip()
		sr2 = sr2.strip()
		if not (sr1 in to_remove or sr2 in to_remove):
			reduced.write(edge + '\n')
			nodes.add(sr1)
			nodes.add(sr2)
			num_new_edges += 1

	reduced.close()

	original_name = fname.split("/")[-1].strip() or fname.split("/")[-2].strip()
	info.write(original_name + ' ====> ' + new_name + '\n')
	info.write('\tNum nodes:' + str(len(nodes)) + '\n')
	info.write('\tNum edges:' + str(num_new_edges) + '\n')
	info.write('\n')


limits = [10, 50, 100, 500, 1000]

for limit in limits:
	print "==============", limit, "=============="
	reduce_network("final-user-networks/comment_unweighted.tsv", "final-user-networks/comment_unweighted_node_degrees.tsv", limit)
	reduce_network("final-user-networks/comment_weighted.tsv", "final-user-networks/comment_weighted_node_degrees.tsv", limit)
	reduce_network("final-user-networks/submission_unweighted.tsv", "final-user-networks/submission_unweighted_node_degrees.tsv", limit)
	reduce_network("final-user-networks/submission_weighted.tsv", "final-user-networks/submission_weighted_node_degrees.tsv", limit)
	reduce_network("final-user-networks/user_unweighted.tsv", "final-user-networks/user_unweighted_node_degrees.tsv", limit)
	reduce_network("final-user-networks/user_weighted.tsv", "final-user-networks/user_weighted_node_degrees.tsv", limit)
	print ""
		

