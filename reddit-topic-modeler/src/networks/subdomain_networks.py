'''
Methods to create subdomain-based networks.

1) network with no edges filtered out. Also creates
tf-idf subdomain stats. Input: subdomain information file,
with the following format:
subdomain \t subreddit1, subredddit2...subredditn \t weight1,weight2...weightn
chrisfelizzi.bandcamp.com       postrock,TheseAreOurAlbums      1,1
Output: raw network with average edge weights and tf-idf edge weights


2) network with edges filtered out based on nodes
with certain tf-idf. Input: tf-idf score on which
to filter.
'''

import sys
import math

log_interval = 5000

def raw_network(subdomain_info_file):
	subdomain_info = open(subdomain_info_file).read().splitlines()

	num_subdomains = 0

	print 'Aggregating urls per subreddit...'

	# Aggregate number of urls each subreddit has used
	nodes = {}
	for x, line in enumerate(subdomain_info):

		if x % log_interval == 0:
			print "Progress::::", x / float(len(subdomain_info)) * 100, "%"

		try:
			_, subredditstr, weightstr = line.split('\t')
		except ValueError:
			print "ValError::::", line
			continue

		subreddits = subredditstr.split(',')
		weights = map(lambda w: int(w), weightstr.split(','))
		for i, subreddit in enumerate(subreddits):
			try:
				nodes[subreddit] += weights[i]
			except KeyError:
				nodes[subreddit] = weights[i]

		num_subdomains += sum(weights)

	num_subreddits = len(nodes)
	print num_subreddits, "nodes (unique subreddits)"

	network = {}

	print "Creating full subdomain network..."

	# Save tf-idf information. Format: domain \t idf \t subreddit \t tf-idf
	tf_idf_file = open("../data/networks/final_tf-idf_subdomain_info.tsv", "w")

	# Save all possible edges. Format: domain \t subreddit1 \t subreddit2 \t weight1 \t weight2
	all_edges = open("../data/networks/final_all_subdomain_edges.tsv", "w")

	for x, line in enumerate(subdomain_info):

		if x % log_interval == 0:
			print "Progress::::", x / float(len(subdomain_info)) * 100, "%"

		try:
			subdomain, subredditstr, weightstr = line.split('\t')
		except ValueError:
			print "ValError::::", line
			continue
		subreddits = subredditstr.split(',')
		weights = map(lambda w: int(w), weightstr.split(','))

		idf = math.log(float(num_subreddits) / float(len(subreddits)))

		for i, subreddit in enumerate(subreddits):
			tf = weights[i] / float(nodes[subreddit])
			tf_idf = tf * idf

			tfidfstr = "\t".join([subdomain, str(idf), subreddit, str(tf_idf)]) + "\n"
			tf_idf_file.write(tfidfstr)

			for j, subreddit2 in enumerate(subreddits):

				if j > i:
					# Add edge
					edge = (subreddit, subreddit2)
					avg = (weights[i] + weights[j]) / 2.0
					try:
						network[edge] += avg
					except KeyError:
						inverse = (subreddit2, subreddit)
						try:
							network[inverse] += avg
						except KeyError:
							network[edge] = avg

					all_edges.write("\t".join([subdomain, subreddit, subreddit2, str(weights[i]), str(weights[j])]))


	tf_idf_file.close()
	all_edges.close()

	# Save raw network
	networkf = open("../data/networks/final_subdomain_full_network.tsv", "w")
	for edge, weight in network.iteritems():
		networkf.write("\t".join([edge[0], edge[1], str(weight)]))

	networkf.close()

	num_edges = len(network)

	infofile = open("../data/networks/subdomain_details.txt", "w")
	infofile.write("Number of nodes (subreddits) in full subdomain network: " + str(num_subreddits) + "\n")
	infofile.write("Number of edges in subdomain network: " + str(num_edges) + "\n")
	infofile.write("Total number of subdomains: " + str(num_subdomains) + "\n")
	infofile.write("Number of unique subdomains: " + str(len(subdomain_info)) + "\n")
	infofile.write("Note: Full subdomain network weighted by average link count between two subreddits.\n")
	infofile.close()

# The higher the tf-idf, the better, since log(#subreddits / #subreddits with url)
# goes to 0 as a url appears in more and more subreddits. This is scaled by frequency
# of the url in that subreddit. So if it appears a lot in the subreddit, it will have
# a frequency closer to 1 and the idf term will remain the same. If it doesn't appear
# a lot, the idf term will be scaled down considerably.
def reduced_network(edge_file, tf_idf_file, tfidf_thresh):
	edges = open(edge_file).read().splitlines()

	tfidfs = {}
	with open(tf_idf_file) as tif:
		for line in tif:
			domain, idf, subreddit, tfidf = line.split('\t')
			try:
				s = tfidfs[subreddit]
				s[domain] = (tfidf, idf)
			except KeyError:
				tfidfs[subreddit] = {domain: (tfidf, idf)}

	network = {}

	# Build reduced network - omit edge if tfidf is lower than threshold
	for line in edges:
		domain, subreddit1, subreddit2, weight1, weight2 = line.split("\t")

		domains1 = tfidfs[subreddit1][domain]
		domains2 = tfidfs[subreddit2][domain]

		# If the tfidf score is high enough for both, keep the edge
		if domains1[0] >= tfidf_thresh and domains2[0] >= tfidf_thresh:
			edge = (subreddit1, subreddit2)
			avg = (int(weight1) + int(weight2)) / 2.0
			try:
				network[edge] += avg
			except KeyError:
				inverse = (subreddit2, subreddit1)
				try:
					network[inverse] += avg
				except KeyError:
					network[edge] = avg

	# Now save the network
	fname = "subdomain_network_" + str(tfidf_thresh)
	networkf = open("../data/networks")


# If provide a tf-idf threshold, construct reduced network
try:
	tfidf_thresh = int(sys.argv[1])
	edges = "../data/networks/final_all_subdomain_edges.tsv"
	tf_idf_file = "../data/networks/final_tf-idf_subdomain_info.tsv"
	reduced_network(edges, tf_idf_file, tfidf_thresh)
# Otherwise construct full one with tf-idf info
except IndexError:
	raw_network("../data/networks/final_subdomain_info.tsv")