"""
Transform output of a clustering algorithm from indices to subreddit  
strings. Files that result from fast modularity (in C) should end
in .groups; files resulting from the map equation should end in .map. 

Usage:
python elucidate_clusters.py groups key outputd 
"""
# import matplotlib as mpl
# mpl.use("Agg")

import os
import sys
import matplotlib.pyplot as plt

# Optimal sizes 
_opt_min = 3
_opt_max = 100

groupsf = sys.argv[1]
keyf = sys.argv[2]
outputd = sys.argv[3]

key = {}
for line in open(keyf).read().splitlines():
	index, sr = line.split("\t")
	key[index] = sr

def fast_modularity_clusters():
	groups = []
	info = open(groupsf).read().splitlines()
	for i in range(len(info)):
		line = info[i]
		if line.startswith("GROUP"):
			i += 1
			group = []
			while i < len(info) and not info[i].startswith("GROUP"):
				sr = key[info[i]]
				group.append(sr)
				i += 1
			groups.append(group)
	return groups

"""
*Modules 4
1 "Node 13,..." 0.25 0.0395432
2 "Node 5,..." 0.25 0.0395432
3 "Node 9,..." 0.25 0.0395432
4 "Node 1,..." 0.25 0.0395432
*Nodes 16
1:1 "Node 13" 0.0820133
1:2 "Node 14" 0.0790863
1:3 "Node 16" 0.0459137
1:4 "Node 15" 0.0429867
"""


def map_equation_clusters():
	groups = {}
	with open(groupsf, "r") as f:
		reading = False
		linetype = None
		for line in f:
			if line.startswith("*Nodes"):
				linetype = "node"
				continue
			if line.startswith("*Modules"):
				reading = True
				linetype = "module"
				continue
			if line.startswith("*Links"):
				break
			if reading:
				if linetype == "module":
					info = line.split()
					cluster = info[0]
					node = str(int(info[1].split(",")[0].replace('"', '')) - 1)
					groups[cluster] = []
				elif linetype == "node":
					info = line.split()
					cluster = info[0].split(":")[0]
					node = str(int(info[1].replace('"', '')) - 1)
					groups[cluster].append(key[node])
	return groups.values()


if groupsf.endswith(".groups"):
	groups = fast_modularity_clusters()
elif groupsf.endswith(".map"):
	groups = map_equation_clusters()

if not outputd.endswith("/"):
	outputd += "/"

component = groupsf.split("/")[-1].split(".")[0]
fname = component + '.clusters'
fname_opt = component + '_best.clusters'
outputf = open(os.path.join(outputd, fname), "w")
optf = open(os.path.join(outputd, fname_opt), "w")

for group in groups:
	outputf.write("GROUP " + str(len(group)) + "\n")
	for sr in group:
		outputf.write(sr + "\n")
	outputf.write("\n")
outputf.close()

# Put all groups that have a certain optimal size
# in a separate file for ease of viewing
best = filter(lambda group : len(group) >= _opt_min and len(group) <= _opt_max, groups)
for group in best:
	optf.write("GROUP " + str(len(group)) + "\n")
	for sr in group:
		optf.write(sr + "\n")
	optf.write("\n")
optf.close()

# MAKE PIE PLOTS 

# pltname1 = fname.replace(".txt", "_pie.png")
# pltname2 = fname.replace(".txt", "_pie_small.png")

# Show cluster size information in pie graphs 
# raw_sizes = map(lambda group : len(group), groups)
# total = float(sum(raw_sizes))
#
# hist = {}
# for s in raw_sizes:
# 	try:
# 		hist[s] += 1
# 	except KeyError:
# 		hist[s] = 1
#
# # Print some stats
# print "Number of size 1-2 clusters:", hist[1]+hist[2]
# print "Largest cluster size:", max(hist.keys())
# print "Percentage of subreddits in size 1-2 clusters:", ((hist[1]+hist[2]) / total)*100, "%"
# print "Percentage of subreddits in largest cluster:", (max(hist.keys()) / total)*100, "%"
# print "Total number of subreddits in this component:", total
#
# # Only plot those above min
# sizes = filter(lambda k: k > _opt_min, hist.keys())
# percentages = map(lambda s : hist[s], sizes)
#
# colors = ["yellowgreen", "gold", "lightskyblue", "lightcoral", "mintcream", "plum"]

# Save the pie plot 
# plt.pie(percentages, labels=sizes, autopct='%1.1f%%', shadow=False, colors=colors)
# plt.axis("equal")
# plt.savefig(outputd + pltname1)



# Take out the size with the most members 
# i = percentages.index(max(percentages))
# print i, sizes[i]
# sizes = sizes[:i] + sizes[i+1:]
# percentages = percentages[:i] + percentages[i+1:]

# # Replot 
# plt.pie(percentages, labels=sizes, autopct='%1.1f%%', shadow=False)
# plt.savefig(outputd + pltname2)

