# Some wikipedia pages are category names...but not all. 
# Others are close (list of Fitzgerald novels is a category...)
#
# Merge the wikipedia taxonomy and reddit's subreddits in 
# 2 ways: 1) ranking networks and 2) combining networks
#
# Usage: python merge_wiki_reddit_by_networks.py network_dir output_file.txt

import os 
import sys
import networkx as nx  

def init_network(fp):
	graph = nx.Graph()
	with fp as lines:
		for line in lines:
			try:
				sr1, sr2, weight = line.split('\t')
				weight = float(weight)
			except ValueError:
				# In case of related network 
				try:
					sr1, sr2 = line.split('\t')
					weight = 1 	# ?? 
				except ValueError:
					print "bad line:", line
					continue 
			graph.add_edge(sr1.strip(), sr2.strip(), weight=weight)
	return graph 


# Get directory containing all the networks. 
# Should only have one network of each type
network_dir = sys.argv[1]

# Initialize the networks 
related_lines = open(os.path.join(network_dir, 'related.network'))
#user_lines = open(os.path.join(network_dir, 'user.network'))
submission_lines = open(os.path.join(network_dir, 'submission.network'))
comment_lines = open(os.path.join(network_dir, 'comment.network'))
xpost_lines = open(os.path.join(network_dir, 'xpost.network'))
subdomain_lines = open(os.path.join(network_dir, 'subdomain.network'))

print "Initializing different network types..."
related_network = init_network(related_lines)
print "Done related:", len(related_network.nodes()), "nodes"
xpost_network = init_network(xpost_lines)
print "Done xpost.", len(xpost_network.nodes()), "nodes"
# user_network = init_network(user_lines)
# print "Done user.", len(user_network.nodes()), "nodes"
submission_network = init_network(submission_lines)
print "Done submission.", len(submission_network.nodes()), "nodes"
comment_network = init_network(comment_lines)
print "Done comment.", len(comment_network.nodes()), "nodes"
subdomain_network = init_network(subdomain_lines)
print "Done subdomain.", len(subdomain_network.nodes()), "nodes"

print "Reading in wikipage matches..."
# Go through and index subreddits that have a matching wiki page 
# Also collect stats. 
wiki_matches = {}
wiki_match_info = {
	"num_in_network": 0,
	"num_not_in_network": 0,
	"num_in_related_network": 0,
	"num_in_xpost_network": 0,
	#"num_in_user_network": 0,
	"num_in_submission_network": 0,
	"num_in_comment_network": 0,
	"num_in_subdomain_network": 0
}
matched = open("subreddit-to-wiki.unambiguous.tsv").read().splitlines()
for line in matched:
	subreddit_url, wiki_url = line.split('\t')
	
	subreddit = subreddit_url.split('/')[-1].strip()
	wiki = ' '.join(wiki_url.split('/')[-1].strip().split('_')).lower()

	try:
		wiki_matches[subreddit].append(wiki)
	except KeyError:
		wiki_matches[subreddit] = [wiki]

	inNetwork = False 

	if related_network.has_node(subreddit):
		wiki_match_info["num_in_related_network"] += 1
		inNetwork = True 

	if xpost_network.has_node(subreddit):
		wiki_match_info["num_in_xpost_network"] += 1
		inNetwork = True

	# if user_network.has_node(subreddit):
	# 	wiki_match_info["num_in_user_network"] += 1
	# 	inNetwork = True

	if submission_network.has_node(subreddit):
		wiki_match_info["num_in_submission_network"] += 1
		inNetwork = True 

	if comment_network.has_node(subreddit):
		wiki_match_info["num_in_comment_network"] += 1
		inNetwork = True

	if subdomain_network.has_node(subreddit):
		wiki_match_info["num_in_subdomain_network"] += 1
		inNetwork = True

	if inNetwork:
		wiki_match_info["num_in_network"] += 1
	else:
		wiki_match_info["num_not_in_network"] += 1

print "Done reading wikipage matches:", len(wiki_matches), "matches to begin with."

# Output files
outf = sys.argv[2]

# For info 
out = open(outf, 'w')
# Different files for the two heuristics 
out_h1 = open(outf.replace('.txt', '_heuristic1.txt'), 'w')
out_h2 = open(outf.replace('.txt', '_heuristic2.txt'), 'w')

# Go through unmatched subreddits and try to find match 
raw_unmatched = open("unmatched-subreddits.by-volume.tsv").read().splitlines()

# Those that aren't present in any network won't be able to be merged. 
# Keep track of them here. 
unmatched_out = open(outf.replace(".txt", "_unmatched.txt"), 'w')

# Have very explicit variables for tallying stats 
num_in_network = 0
num_not_in_network = 0
num_in_related_network = 0
num_in_xpost_network = 0
#num_in_user_network = 0
num_in_submission_network = 0
num_in_comment_network = 0
num_in_subdomain_network = 0
volume_in_related_network = 0
volume_in_xpost_network = 0
#volume_in_user_network = 0
volume_in_submission_network = 0
volume_in_comment_network = 0
volume_in_subdomain_network = 0
volume_in_network = 0
volume_not_in_network = 0
total_volume = 0

# Of subreddits present in network:
num_matches = 0		
volume_matched = 0	

# Used to calculate average number of wiki matches found in 
# an unmatched ==> matched subreddit's neighbors. 
total_wiki_matches = 0

num_matched_related = 0
num_matched_xpost = 0
num_matched_submission = 0
num_matched_comment = 0
num_matched_subdomain = 0
#num_matched_other = 0

# Used to calculate average winning heuristic values 
total_max_weight = 0
total_max_ratio = 0

# Will contain unmatched subreddits present in network, with potential to be matched 
unmatched = []

print "Going through unmatched to collect stats..."

# Get some stats 
for line in raw_unmatched: 
	volume, subreddit = line.split('\t')
	subreddit = subreddit.strip()
	volume = int(volume.strip())

	total_volume += volume 

	inNetwork = False 

	if related_network.has_node(subreddit):
		num_in_related_network += 1
		volume_in_related_network += volume 
		unmatched.append(line)
		inNetwork = True 

	if xpost_network.has_node(subreddit):
		num_in_xpost_network += 1
		volume_in_xpost_network += volume 
		if not inNetwork:
			unmatched.append(line)
		inNetwork = True

	# if user_network.has_node(subreddit):
	# 	num_in_user_network += 1
	# 	volume_in_user_network += volume 
	# 	if not inNetwork:
	# 		unmatched.append(line)
	# 	inNetwork = True 

	if submission_network.has_node(subreddit):
		num_in_submission_network += 1
		volume_in_submission_network += volume 
		if not inNetwork:
			unmatched.append(line)
		inNetwork = True 

	if comment_network.has_node(subreddit):
		num_in_comment_network += 1
		volume_in_comment_network += volume 
		if not inNetwork:
			unmatched.append(line)
		inNetwork = True 

	if subdomain_network.has_node(subreddit):
		num_in_subdomain_network += 1
		volume_in_subdomain_network += volume 
		if not inNetwork:
			unmatched.append(line)
		inNetwork = True

	if inNetwork:
		num_in_network += 1
		volume_in_network += volume 
	else:
		num_not_in_network += 1
		volume_not_in_network += volume 
		unmatched_out.write(line + '\n')

# unmatched now contains all unmatched subreddits present in network
# that could be matched. left_to_match will be the dynamic list of 
# subreddits being matched or not. 
left_to_match = unmatched[:]

num_iter = len(unmatched) * 3
iter_num = num_iter 

print "Starting iteration with", num_iter, "iterations!"

out.write('Number of iterations: ' + str(num_iter) + '\n')

def match(network, subreddit, network_type, weighted=True):
	global num_matches, total_wiki_matches, volume_matched , wiki_matches 
	global total_max_weight, total_max_ratio 

	neighbors = network.adj[subreddit]
	neighbor_matches = filter(lambda neighbor: neighbor in wiki_matches, neighbors.keys())
	if neighbor_matches:
		num_matches += 1
		total_wiki_matches += len(neighbor_matches)
		volume_matched += volume 

		wiki_matches[subreddit] = neighbor_matches

		if weighted:
			neighbor_weights = map(lambda neighbor: network[neighbor][subreddit]['weight'], neighbor_matches)
			neighbor_degrees = map(lambda neighbor: network.degree(neighbor), neighbor_matches)

			# Heuristic one: highest edge weight 
			max_weight = max(neighbor_weights)
			best_neighbor_h1 = neighbor_matches[neighbor_weights.index(max_weight)]
			total_max_weight += max_weight 

			out_h1.write(subreddit + '\t' + best_neighbor_h1 + '\t' + network_type + '\t' + str(max_weight) + '\n')

			# Heuristic two: highest edge weight : node degree ratio 
			ratios = [w / float(neighbor_degrees[i]) for i, w in enumerate(neighbor_weights)]
			max_ratio = max(ratios)
			best_neighbor_h2 = neighbor_matches[ratios.index(max_ratio)]
			total_max_ratio += max_ratio

			out_h2.write(subreddit + '\t' + best_neighbor_h2 + '\t' + network_type + '\t' + str(max_ratio) + '\n')

		else:
			# Just write out the first match for simplicity 
			out_h1.write(subreddit + '\t' + neighbor_matches[0] + '\t' + network_type + '\t' + str(len(neighbor_matches)) + '\n')
			out_h2.write(subreddit + '\t' + neighbor_matches[0] + '\t' + network_type + '\t' + str(len(neighbor_matches)) + '\n')
		return True 

while len(left_to_match) > 0 and iter_num > 0:
	# Update me of progress 
	iter_num -= 1
	if iter_num % 5000 == 0:
		print "Progress::::", ((num_iter - iter_num) / float(num_iter)) * 100, "%"
		print num_matches, "matched", "out of", len(unmatched)
		print ""

	# Get volume and subreddit 
	line = left_to_match.pop()
	volume, subreddit = line.split('\t')
	subreddit = subreddit.strip()
	volume = int(volume.strip()) 

	# Give priority to related network, since this is hand-curated 
	# Related network doesn't rely on weights, so don't worry about this. 
	if related_network.has_node(subreddit):
		if match(related_network, subreddit, 'related', weighted=False):
			num_matched_related += 1
			continue 

	# If have arrived here means couldn't find anything in related network. 
	# Now try to find something in xpost network. 
	if xpost_network.has_node(subreddit):
		if match(xpost_network, subreddit, 'xpost'):
			num_matched_xpost += 1
			continue
	
	# Now try to find something in submission user network
	if submission_network.has_node(subreddit):
		if match(submission_network, subreddit, 'submission'):
			num_matched_submission += 1
			continue 

	# Try comment user network 
	if comment_network.has_node(subreddit):
		if match(comment_network, subreddit, 'comment'):
			num_matched_comment += 1
			continue 

	# Give last priority to subdomain network 
	if subdomain_network.has_node(subreddit):
		if match(subdomain_network, subreddit, 'subdomain'):
			num_matched_subdomain += 1
			continue

	# If subreddit wasn't found in any of the networks, re-add to list for the next iteration 
	left_to_match = [line] + left_to_match


out_h1.close()
out_h2.close()

# Update unmatched file and tally proportion of volume that's unmatched 
volume_unmatched = 0
for unmatched_line in left_to_match:
	volume_unmatched += int(unmatched_line.split('\t')[0].strip())
	unmatched_out.write(unmatched_line + '\n')
unmatched_out.close()

############## Print/save stats ##############

### Wiki match stats
perc_wiki_in_network = "{0:.2f}".format((wiki_match_info['num_in_network'] / float(len(wiki_matches))) * 100)
perc_wiki_not_in_network  = "{0:.2f}".format((wiki_match_info['num_not_in_network'] / float(len(wiki_matches))) * 100)
perc_wiki_in_related = "{0:.2f}".format((wiki_match_info['num_in_related_network'] / float(wiki_match_info['num_in_network'])) * 100)
perc_wiki_in_xpost = "{0:.2f}".format((wiki_match_info['num_in_xpost_network'] / float(wiki_match_info['num_in_network'])) * 100)
#perc_wiki_in_user = "{0:.2f}".format((wiki_match_info['num_in_user_network'] / float(wiki_match_info['num_in_network'])) * 100)
perc_wiki_in_submission = "{0:.2f}".format((wiki_match_info['num_in_submission_network'] / float(wiki_match_info['num_in_network'])) * 100)
perc_wiki_in_comment = "{0:.2f}".format((wiki_match_info['num_in_comment_network'] / float(wiki_match_info['num_in_network'])) * 100)
perc_wiki_in_subdomain= "{0:.2f}".format((wiki_match_info['num_in_subdomain_network'] / float(wiki_match_info['num_in_network'])) * 100)

out.write("Wikipages match stats:\n")
out.write("Number of wikipage-subreddit matches: " + str(len(wiki_matches)) + "\n")
out.write("Number of wikipage-subreddit matches present in networks: " + str(wiki_match_info['num_in_network']) + "\t" + str(perc_wiki_in_network) + "%\n")
out.write("\tRelated: " + str(wiki_match_info['num_in_related_network']) + "\t" + str(perc_wiki_in_related) + "%\n")
out.write("\tXpost: " + str(wiki_match_info['num_in_xpost_network']) + "\t" + str(perc_wiki_in_xpost) + "%\n")
#out.write("\tUser: " + str(wiki_match_info['num_in_user_network']) + "\t" + str(perc_wiki_in_user) + "%\n")
out.write("\tSubmission: " + str(wiki_match_info['num_in_submission_network']) + "\t" + str(perc_wiki_in_submission) + "%\n")
out.write("\tComment: " + str(wiki_match_info['num_in_comment_network']) + "\t" + str(perc_wiki_in_comment) + "%\n")
out.write("\tSubdomain: " + str(wiki_match_info['num_in_subdomain_network']) + "\t" + str(perc_wiki_in_subdomain) + "%\n")
out.write("Number of wikipages-subreddit matches NOT present in networks: " + str(wiki_match_info['num_not_in_network']) + "\t" + str(perc_wiki_not_in_network) + "%\n")
out.write("")

### Higher level stats 
perc_in_network = "{0:.2f}".format((len(unmatched) / float(len(raw_unmatched))) * 100)
perc_not_in_network = "{0:.2f}".format((num_not_in_network / float(len(raw_unmatched))) * 100)
perc_volume_in_network = "{0:.2f}".format((volume_in_network / float(total_volume)) * 100)
perc_volume_not_in_network = "{0:.2f}".format((volume_not_in_network / float(total_volume)) * 100)

### Of those in network... 
perc_matched = "{0:.2f}".format((num_matches / float(len(unmatched))) * 100)
perc_left = "{0:.2f}".format((len(left_to_match) / float(len(unmatched))) * 100)
perc_matched_volume = "{0:.2f}".format((volume_matched / float(volume_in_network)) * 100)
perc_unmatched_volume = "{0:.2f}".format((volume_unmatched / float(volume_in_network)) * 100)

# Network breakdown (note: includes overlaps)
perc_in_related = "{0:.2f}".format((num_in_related_network / float(num_in_network)) * 100)
perc_in_xpost = "{0:.2f}".format((num_in_xpost_network / float(num_in_network)) * 100)
#perc_in_user = "{0:.2f}".format((num_in_user_network / float(num_in_network)) * 100)
perc_in_submission = "{0:.2f}".format((num_in_submission_network / float(num_in_network)) * 100)
perc_in_comment = "{0:.2f}".format((num_in_comment_network / float(num_in_network)) * 100)
perc_in_subdomain = "{0:.2f}".format((num_in_subdomain_network / float(num_in_network)) * 100)
perc_vol_in_related = "{0:.2f}".format((volume_in_related_network / float(volume_in_network)) * 100)
perc_vol_in_xpost = "{0:.2f}".format((volume_in_xpost_network / float(volume_in_network)) * 100)
#perc_vol_in_user = "{0:.2f}".format((volume_in_user_network / float(volume_in_network)) * 100)
perc_vol_in_submission = "{0:.2f}".format((volume_in_submission_network / float(volume_in_network)) * 100)
perc_vol_in_comment = "{0:.2f}".format((volume_in_comment_network / float(volume_in_network)) * 100)
perc_vol_in_subdomain = "{0:.2f}".format((volume_in_subdomain_network / float(volume_in_network)) * 100) 

# Matching breakdown (no overlap)
perc_related_matches = "{0:.2f}	".format((num_matched_related / float(num_matches)) * 100)
perc_xpost_matches = "{0:.2f}".format((num_matched_xpost / float(num_matches)) * 100)
perc_submission_matches = "{0:.2f}".format((num_matched_submission / float(num_matches)) * 100)
perc_comment_matches = "{0:.2f}".format((num_matched_comment / float(num_matches)) * 100)
perc_subdomain_matches = "{0:.2f}".format((num_matched_subdomain / float(num_matches)) * 100)
#perc_other_matches = "{0:.2f}".format((num_matched_other / float(num_matches)) * 100)

out.write("Number to match (to start with): " + str(len(raw_unmatched)) + "\n")
out.write("Number of unmatched subreddits present in networks: " + str(len(unmatched)) + "\t" + str(perc_in_network) + "%\n")
out.write("\tBy volume: " + str(volume_in_network) + "\t" + str(perc_volume_in_network) + "%\n")
out.write("\tRelated: " + str(num_in_related_network) + "\t" + str(perc_in_related) + "%\n")
out.write("\t\tVolume: " + str(volume_in_related_network) + "\t" + str(perc_vol_in_related) + "%\n")
out.write("\tXpost: " + str(num_in_xpost_network) + "\t" + str(perc_in_xpost) + "%\n")
out.write("\t\tVolume: " + str(volume_in_xpost_network) + "\t" + str(perc_vol_in_xpost) + "%\n")
# out.write("\tUser: " + str(num_in_user_network) + "\t" + str(perc_in_user) + "%\n")
# out.write("\t\tVolume: " + str(volume_in_user_network) + "\t" + str(perc_vol_in_user) + "%\n")
out.write("\tSubmission: " + str(num_in_submission_network) + "\t" + str(perc_in_submission) + "%\n")
out.write("\t\tVolume: " + str(volume_in_submission_network) + "\t" + str(perc_vol_in_submission) + "%\n")
out.write("\tComment: " + str(num_in_comment_network) + "\t" + str(perc_in_comment) + "%\n")
out.write("\t\tVolume: " + str(volume_in_comment_network) + "\t" + str(perc_vol_in_comment) + "%\n")
out.write("\tSubdomain: " + str(num_in_subdomain_network) + "\t" + str(perc_in_subdomain) + "%\n")
out.write("\t\tVolume: " + str(volume_in_subdomain_network) + "\t" + str(perc_vol_in_subdomain) + "%\n")
out.write("Number of unmatched subreddits NOT present in networks: " + str(num_not_in_network) + "\t" + str(perc_not_in_network) + "%\n")
out.write("\tBy volume: " + str(volume_unmatched) + "\t" + str(perc_volume_not_in_network) + "%\n")
out.write("\n")
out.write("Out of unmatched subreddits present in networks:\n")
out.write("Number matched: " + str(num_matches) + "\t" + str(perc_matched) + "%\n")
out.write("\tVolume: " + str(volume_matched) + "\t" + str(perc_matched_volume) + "\n")
out.write("\tUsing related network: " + str(num_matched_related) + "\t" + str(perc_related_matches) + "%\n")
out.write("\tUsing xpost network: " + str(num_matched_xpost) + "\t" + str(perc_xpost_matches) + "%\n")
out.write("\tUsing submission network: " + str(num_matched_submission) + "\t" + str(perc_submission_matches) + "%\n")
out.write("\tUsing comment network: " + str(num_matched_comment) + "\t" + str(perc_comment_matches) + "%\n")
out.write("\tUsing subdomain network: " + str(num_matched_subdomain) + "\t" + str(perc_subdomain_matches) + "%\n")
#out.write("\tUsing xpost/user networks: " + str(num_matched_other) + "\t" + str(perc_other_matches) + "%\n")
out.write("Number left to match: " + str(len(left_to_match)) + "\t" + str(perc_left) + "%\n")
out.write("\tVolume: " + str(volume_unmatched) + "\t" + str(perc_unmatched_volume) + "%\n")
out.write("\n")

# Heuristic stats 
average_max_weight = (total_max_weight / float(num_matches)) * 100
average_max_ratio = (total_max_ratio / float(num_matches)) * 100

out.write("Heuristic stats:\n")
out.write("Average max weight: " + str(average_max_weight) + "\n")
out.write("Average max ratio: " + str(average_max_ratio) + "\n")
out.write("\n")
 
# Average number of wiki matches found in unmatched ==> matched subreddit's neighbors
average_wiki_matches = total_wiki_matches / float(num_matches) * 100
out.write("Average number of matching neighbors found during match: " + str(average_wiki_matches) + "\n")

out.close()

os.system("cat " + outf)

