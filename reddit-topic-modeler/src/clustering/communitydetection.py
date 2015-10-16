"""
Run fast community detection algorithm on all connected components
of a given directory.

./FastCommunity_wMH -f ../../../data/clustering/nov15_10000/component0.wpairs -l firstRun
"""

import os
import sys

CCdir = sys.argv[1]
out = os.path.join(CCdir, 'fcd_results')
component_files = os.listdir(CCdir)

os.system('mkdir ' + out)


for f in component_files:
	if f.endswith('.wpairs') and '-fc_' not in f:

		path = os.path.join(CCdir, f)

		# Get mapping info
		num = f.split('.wpairs')[0].split('component')[1]
		print "=============="
		print f, num
		print "=============="
		groups = os.path.join(CCdir, 'component' + num + '-fc_first.groups')
		mapping = os.path.join(CCdir, '../mappings', 'mapping' + num + '.txt')

		# Run the FCD clustering - first step
		command1 = 'clustering/FastCommunity_weighted/FastCommunity_wMH -f ' + path + ' -l first'
		os.system(command1)

		# Find the maximum modularity in generated info file
		# ex: component1-fc_first.info
		infopath = os.path.join(CCdir, f.replace('.wpairs', '-fc_first.info'))
		info = open(infopath).read().splitlines()
		max_modularity = '0'
		for line in info:
			if line.startswith('STEP------'):
				max_modularity = line.split('\t')[1].strip()
				break

		# Too small or something. Just get the connected component.
		if max_modularity == '0':
			key = {}
			for line in open(mapping).read().splitlines():
				index, sr = line.split('\t')
				key[index] = sr
			cc_edges = open(path).read().splitlines()
			output_group = open(os.path.join(out, 'component' + num + '.clusters'), 'w')
			group = {}
			for edge in cc_edges:
				s1, s2, weight = edge.split('\t')
				sr1 = key[s1]
				sr2 = key[s2]
				group[sr1] = 1
				group[sr2] = 1
			output_group.write("GROUP " + str(len(group)) + "\n")
			for k, v in group.iteritems():
				output_group.write(k + "\n")
			output_group.close()
			continue

		# Run the second FCD step
		command2 = 'clustering/FastCommunity_weighted/FastCommunity_wMH -f ' + path + ' -l first' + ' -c ' + max_modularity
		os.system(command2)

		print command2

		# Find the clusters
		cluster_command = 'python elucidate_clusters.py ' + groups + ' ' + mapping + ' ' + out
		os.system(cluster_command)


