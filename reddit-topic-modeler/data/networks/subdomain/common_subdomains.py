"""
Rank subdomains by how common they are - i.e, order by 
subdomain IDF in  ascending order, since the lower the 
IDF score, the more common the subdomain is). 

Rank edges by how unimportant they are - i.e., order by 
tf-idf in ascending order, since the lower the tf-idf 
score, the less important that edge is. 
"""

def by_idf():
	# Format: domain \t idf \t subreddit \t tf-idf 
	lines = open("final_tf-idf_subdomain_info.tsv").read().splitlines()

	domains_by_idf = set()
	for line in lines:
		try:
			domain, idf, subreddit, tfidf = line.split("\t")
			domains_by_idf.add((float(idf), domain))
		except ValueError:
			print 'bad line:', line 
			continue 

	output = list(domains_by_idf)
	output.sort()

	for idf, domain in output:
		print idf, '\t', domain 

def by_tfidf():
	# Format: domain \t idf \t subreddit \t tf-idf 
	lines = open("final_tf-idf_subdomain_info.tsv").read().splitlines()

	edges_by_tfidf = set()
	for line in lines:
		domain, idf, subreddit, tfidf = line.split("\t")
		edges_by_tfidf.add((float(tfidf), domain, subreddit))

	output = list(edges_by_tfidf)
	output.sort()

	for tfidf, subdomain, subreddit in output:
		print tfidf, '\t', subdomain, '\t', subreddit 

by_tfidf()
