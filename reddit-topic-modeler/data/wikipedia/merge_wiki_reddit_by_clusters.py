# Some wikipedia pages are category names...but not all. 
# Others are close (list of Fitzgerald novels is a category...)

import os 
import sys
import networkx as nx 

class WikiGraph:

	def __init__(self, cluster_dir_by_type):
		self.subreddits = {}
		self.graph = nx.Graph()

		# All the clusters a subreddit belongs to will be indexed 
		# by the subreddit. Each cluster has a 0-indexed unique id.
		subreddits = {}
		group_id = 0

		print "Grouping clusters..."

		# Each type of cluster file should be in separate dirs. 
		# Dir should be named after the type (ex: user, xpost, etc).
		for cluster_dir in os.listdir(cluster_dir_by_type):
			if not cluster_dir.startswith('.'):
				path = os.path.join(cluster_dir_by_type, cluster_dir)
				print path
				cluster_files = os.listdir(path)
				# Go through each cluster file
				for cf in cluster_files:
					cluster_path = os.path.join(path, cf)
					# Parse cluster 
					info = open(cluster_path).read().splitlines()
					for i in range(len(info)):
						line = info[i]
						if line.startswith("GROUP"):
							i += 1
							group = []
							while i < len(info) and not info[i].startswith("GROUP"):
								sr = info[i].strip()
								group.append(sr)
								i += 1
							for sr in group:
								try:
									s = subreddits[sr].append((group_id, group, cluster_dir))
								except KeyError:
									subreddits[sr] = [(group_id, group, cluster_dir)]
							group_id += 1

		print "Creating wikipedia graph..."
		wiki_pages = open("WiBi.pagetaxonomy.ver1.0.txt").read().splitlines()
		wiki_categories = open("WiBi.categorytaxonomy.ver1.0.txt").read().splitlines()

		## TODO: MAKE DIRECTED 
		graph = nx.Graph()

		print "\tGoing through wikipages..."
		for page_edge in wiki_pages:
			# Skip commented lines 
			if page_edge.startswith("#"):
				continue
			page, category = page_edge.split("\t")
			graph.add_edge(page.strip().lower(), category.strip().lower(), subreddits={})

		print "\tGoing through categories..."
		for category_edge in wiki_categories:
			# Skip commented lines 
			if category_edge.startswith("#"):
				continue
			c1, c2 = category_edge.split("\t")
			graph.add_edge(c1.strip().lower(), c2.strip().lower(), subreddits={})	

		print "Adding direct (unambiguous) subreddit matches to wiki graph..."
		matched = open("subreddit-to-wiki.unambiguous.tsv").read().splitlines()
		for line in matched:
			subreddit_url, wiki_url = line.split('\t')
			
			subreddit = subreddit_url.split('/')[-1].strip()
			wiki = ' '.join(wiki_url.split('/')[-1].strip().split('_')).lower()

			if graph.has_node(wiki):
				print wiki, 'is node in graph corresponding to:::', subreddit 
				try:
					graph.node[wiki]['subreddits'].add(subreddit)
				except KeyError:
					graph.node[wiki]['subreddits'] = set(subreddit)

	# def load_unmatched():
	# 	unmatched = open("unmatched-subreddits-by-volume.tsv").read().splitlines()
	# 	for line in unmatched: 
	# 		volume, subreddit = line.split('\t')
	# 		subreddit = subreddit.strip()
	# 		if subreddit in subreddits:
	# 			subreddits[subreddit]

# Directory containing all the clusters, ever 
#cluster_dir_by_type = sys.argv[1]

#wg = WikiGraph('clusters')

# print "Merging unmatched subreddits..."
# print "TODO: Merge ambiguous subreddit matches."

outf = sys.argv[1]
out = open(outf, 'w')

cluster_type_ranking = {"user": 2, "xpost": 3, "related": 1, "subdomain": 4}

# All the clusters a subreddit belongs to will be indexed 
# by the subreddit. Each cluster has a 0-indexed unique id.
subreddits = {}
group_id = 0

print "Grouping clusters..."

cluster_dir_by_type = 'clusters'

# Each type of cluster file should be in separate dirs. 
# Dir should be named after the type (ex: user, xpost, etc).
for cluster_dir in os.listdir(cluster_dir_by_type):
	if not cluster_dir.startswith('.'):
		path = os.path.join(cluster_dir_by_type, cluster_dir)
		print path
		cluster_files = os.listdir(path)
		# Go through each cluster file
		for cf in cluster_files:
			cluster_path = os.path.join(path, cf)
			# Parse cluster 
			info = open(cluster_path).read().splitlines()
			for i in range(len(info)):
				line = info[i]
				if line.startswith("GROUP"):
					i += 1
					group = []
					while i < len(info) and not info[i].startswith("GROUP"):
						sr = info[i].strip()
						group.append(sr)
						i += 1
					cluster_rank = cluster_type_ranking[cluster_dir]
					for sr in group:
						try:
							s = subreddits[sr].append((cluster_rank, group, group_id, cluster_dir))
						except KeyError:
							subreddits[sr] = [(cluster_rank, group, group_id, cluster_dir)]
					group_id += 1


matches = {}

matched = open("subreddit-to-wiki.unambiguous.tsv").read().splitlines()
for line in matched:
	subreddit_url, wiki_url = line.split('\t')
	
	subreddit = subreddit_url.split('/')[-1].strip()
	wiki = ' '.join(wiki_url.split('/')[-1].strip().split('_')).lower()

	try:
		matches[subreddit].append(wiki)
	except KeyError:
		matches[subreddit] = [wiki]

	# if graph.has_node(wiki):
	# 	print wiki, 'is node in graph corresponding to:::', subreddit 
	# 	try:
	# 		graph.node[wiki]['subreddits'].add(subreddit)
	# 	except KeyError:
	# 		graph.node[wiki]['subreddits'] = set(subreddit)

#unmatched = open("unmatched-subreddits.by-volume.tsv").read().splitlines()
raw_unmatched = open("unmatched-subreddits.by-volume.tsv").read().splitlines()

unmatched_out = open(outf.replace(".txt", "_unmatched.txt"), 'w')

volume_noclusters = 0
volume_clusters = 0
total_volume = 0

unmatched = []

num_in_clusters = 0 		# tallies how many subreddits are actually associated with one or more clusters 
num_no_cluster = 0 			# tallies how many subreddits simply aren't associated with a cluster 

for line in raw_unmatched: 
	volume, subreddit = line.split('\t')
	subreddit = subreddit.strip()
	volume = int(volume.strip())

	total_volume += volume 

	if subreddit in subreddits:
		num_in_clusters += 1
		unmatched.append(line)
		volume_clusters += volume 

	else:
		num_no_cluster += 1
		volume_noclusters += volume
		unmatched_out.write(line + '\n')


# Iteratively proceed 
left_to_match = unmatched[:]

# Want to do more popular ones first? If so, reverse (since will be popping elements)
## TODO: Is this right?? 
unmatched.reverse()

num_matches = 0 			# tallies the number of unmatched->matched we get 
total_cluster_sizes = 0 	# will provide basis for average cluster size that matched an unmatched subreddit 
total_wiki_matches = 0 		# will provide basis for average # of wiki matches in cluster where there's a match 
volume_matched = 0 			# Keeps track of the total submission volume across matches 

# Calculate average cluster size of subreddits that don't get matched 
total_unmatched_cluster_size = 0 
unmatched_cluster_size_denom = 0

num_iter = len(unmatched) * 2
iter_num = num_iter 

print "Number of iterations:", num_iter 
out.write('Number of iterations: ' + str(num_iter) + '\n')

while len(left_to_match) > 0 and iter_num > 0:

	# print "iter_num:", iter_num 
	# print "left to match:", len(left_to_match)

	line = left_to_match.pop()
	iter_num -= 1

	if iter_num % 5000 == 0:
		print "Progress::::", ((num_iter - iter_num) / float(num_iter)) * 100, "%"
		print num_matches, "matched", "out of", len(unmatched)
		print "Average cluster size for unmatched subreddit with match in graph:", total_cluster_sizes / float(num_matches)
		print "Average number of wiki matches in cluster where there's a match:", total_wiki_matches / float(num_matches)
		print ""

	volume, subreddit = line.split('\t')
	subreddit = subreddit.strip()
	volume = int(volume.strip())

	#print "Analyzing:", subreddit 

	if subreddit in subreddits:
		clusters = subreddits[subreddit]

		#print "\tAssociated with", len(clusters), "clusters. Length of first:", len(clusters[0][1]	)

		# Give priority to best-ranked cluster types and smallest clusters 
		clusters.sort(key=lambda c: (c[0], len(c[1])))

		match_found = False 

		for cluster_rank, cluster, cluster_id, cluster_type in clusters:
			wiki_matches = filter(lambda c: c in matches, cluster)

			# TODO: If there are multiple, find closest parent node (from wiki taxonomy)
			if len(wiki_matches) > 0:
				num_matches += 1

				volume_matched += volume

				#print "\t\tHas wiki match:"

				match_found = True 

				# Add to matches 
				matches[subreddit] = []

				total_wiki_matches += len(wiki_matches)
				total_cluster_sizes += len(cluster)

				#print "\t\t\t" + subreddit + '====>  Group#' + str(cluster_id) + "\t" + cluster_type + "\t" + str(len(cluster)) + "\t" + wiki_matches[0]
				out.write(subreddit + '====>  Group#' + str(cluster_id) + "\t" + cluster_type + "\t" + str(len(cluster)) + "\t" + wiki_matches[0] + "\n")
				for match in wiki_matches:
					matches[subreddit].append(match)

				# Just take first match for now 
				break

		if not match_found:
			# print "\t\tNo wiki matches. Readding to list."
			# print "\t\t", clusters[0][1][0], "\t", clusters[0][3]
			left_to_match = [line] + left_to_match
			total_unmatched_cluster_size += sum(map(lambda c: len(c[1]), clusters))
			unmatched_cluster_size_denom += len(clusters)
	#else:
		#print "\tDoesn't have cluster." 
		#left_to_match = [line] + left_to_match 
		#print subreddit, "not part of any cluster"

volume_unmatched = 0

# Update unmatched file 
for unmatched_line in left_to_match:
	volume_unmatched += int(unmatched_line.split('\t')[0].strip())
	unmatched_out.write(unmatched_line + '\n')
unmatched_out.close()

# Print stats 
perc_unmatched_cluster = (num_in_clusters / float(len(raw_unmatched))) * 100
perc_unmatched_nocluster = (num_no_cluster / float(len(raw_unmatched))) * 100 
perc_matched = (num_matches / float(len(unmatched))) * 100
perc_left = (len(left_to_match) / float(len(unmatched))) * 100
perc_cluster_volume = (volume_clusters / float(total_volume)) * 100
perc_nocluster_volume = (volume_noclusters / float(total_volume)) * 100
perc_matched_volume = (volume_matched / float(volume_clusters)) * 100
perc_unmatched_volume = (volume_unmatched / float(volume_clusters)) * 100

print len(subreddits), "subreddits across all clusters"
print "Number of unmatched subreddits to start with:", len(raw_unmatched)
print "\t", num_in_clusters, "associated with at least one cluster\t", perc_unmatched_cluster, "%"
print "\t\tBy volume:", volume_clusters, "\t", perc_cluster_volume, "%"
print "\t", num_no_cluster, "associated with no clusters\t", perc_unmatched_nocluster, "%"
print "\t\tBy volume:", volume_noclusters, "\t", perc_nocluster_volume, "%"
print ""
print "Of those that have associated cluster:"
print "\t", num_matches, "matched\t", perc_matched, "%"
print "\t\tBy volume:", volume_matched, "\t", perc_matched_volume, "%"
print "\t", len(left_to_match), "remain unmatched\t", perc_left, "%"
print "\t\tBy volume:", volume_unmatched, "\t", perc_unmatched_volume, "%"
print ""
print "Average cluster size for unmatched===>matched subreddit:", total_cluster_sizes / float(num_matches)
print "Average number of wiki matches in cluster that resulted in match:", total_wiki_matches / float(num_matches)
print "Average cluster size for subreddits that remain unmatched:", total_unmatched_cluster_size / float(unmatched_cluster_size_denom)


out.write("\n")
out.write(str(len(subreddits)) + " subreddits across all clusters \n")
out.write("Number of unmatched subreddits to start with: " + str(len(unmatched)) + "\n")
out.write("\t" + str(num_in_clusters) + " associated with at least one cluster\t" + str(perc_unmatched_cluster) + "%\n")
out.write("\t\tBy volume: " + str(volume_clusters) + "\t" + str(perc_cluster_volume) + "%\n")
out.write("\t" + str(num_no_cluster) + " associated with no clusters\t" + str(perc_unmatched_nocluster) + "%\n")
out.write("\t\tBy volume: " + str(volume_noclusters) + "\t" + str(perc_nocluster_volume) + "%\n")
out.write("\n")
out.write("Of those that have associated cluster:\n")
out.write("\t" + str(num_matches) + " matched\t" + str(perc_matched) + "%\n")
out.write("\t\tBy volume: " + str(volume_matched) + "\t" + str(perc_matched_volume) + "%\n")
out.write("\t" + str(len(left_to_match)) + " remaine unmatch\t" + str(perc_left) + "%\n")
out.write("\t\tBy volume: " + str(volume_unmatched) + "\t" + str(perc_unmatched_volume) + "%\n")
out.write("\n")
out.write("Average cluster size for unmatched===>matched subreddit: " + str(total_cluster_sizes / float(num_matches)) + "\n")
out.write("Average number of wiki matches in cluster that resulted in match: " + str(total_wiki_matches / float(num_matches)) + "\n")
out.write("Average cluster size for subreddits that remain unmatched: " + str(total_unmatched_cluster_size / float(unmatched_cluster_size_denom)) + "\n")
out.close()

### IDEA: JUST TRY NETWORKS RATHER THAN CLUSTERS 





