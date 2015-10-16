"""
Aggregate clusters across all connected components
and prints out stats about the overall clustering.

Usage: cluster_stats.py <input dir> <output file path>
"""

import os
import sys

d = sys.argv[1]
fs = os.listdir(d)
outf = sys.argv[2]
out = open(outf, 'w')

size_distribution = {}

num_clusters = 0

for f in fs:
	if f.endswith('.clusters') and '_best' not in f:
		clusters = open(os.path.join(d, f)).read().splitlines()
		for line in clusters:
			out.write(line + '\n')
			if line.startswith('GROUP'):
				num_clusters += 1
				size = int(line.split()[1].strip())
				try:
					size_distribution[size] += 1
				except KeyError:
					size_distribution[size] = 1
		out.write('\n')

out.close()

tuples = map(lambda k: (size_distribution[k], k), size_distribution.keys())
tuples.sort(reverse=True)

# Small cluster defined as <5
num_small = 0
# Large cluster defined as >100
num_large = 0

parts = outf.split('/')
infof = parts.pop().split('.')[0] + '_info.txt'
infof = '/'.join(parts) + '/' + infof
info = open(infof, 'w')
info.write('Size \t Num with this size:' + '\n')

num_nodes = 0
for val, size in tuples:
	info.write(str(size) + '\t' + str(val) + '\n')
	if size < 5:
		num_small += 1
	elif size > 100:
		num_large += 1

	num_nodes += (val * size)



info.write("\n")
info.write("Number of clusters: " + str(num_clusters) + '\n')
info.write("Number of nodes: " + str(num_nodes) + '\n')
info.write("Number of clusters smaller than 5: " + str(num_small) + '\n')
info.write("Number of clusters larger than 100: " + str(num_large) + '\n')

info.close()

os.system('cat ' + infof)


