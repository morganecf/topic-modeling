"""
Run Infomap algorithm on all connected components
of a given directory. Output should be a merged
list of clusters.

./Infomap -z --input-format link-list --map ../../../data/clustering/nov15_10000/component0.wpairs ../../../data/clustering/map/nov15_10000
"""

import os
import sys

CCdir = sys.argv[1]
out = os.path.join(CCdir, 'infomap_results')
component_files = os.listdir(CCdir)

os.system('mkdir ' + out)

for f in component_files:
	if f.endswith('.wpairs'):

		path = os.path.join(CCdir, f)

		# Run the infomap clustering
		command = 'clustering/mapequation/Infomap -z --input-format link-list --map ' + path + ' ' + out
		os.system(command)

		# Find the clusters
		num = f.split('.wpairs')[0].split('component')[1]
		groups = os.path.join(out, 'component' + num + '.map')
		mapping = os.path.join(CCdir, '../mappings', 'mapping' + num + '.txt')
		cluster_command = 'python elucidate_clusters.py ' + groups + ' ' + mapping + ' ' + out
		os.system(cluster_command)

		# if f == 'component0.wpairs':
		# 	print f
		# 	print command
		# 	print num
		# 	print groups
		# 	print mapping
		# 	print cluster_command
		# 	print ""





