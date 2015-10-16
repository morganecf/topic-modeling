"""
Create reduced subdomain network based on idf or tf-idf thresholds. 
"""

import sys 

# Edge weights must be greater than or equal to this 
weight_threshold = 5.0

tfidflines = open("final_tf-idf_subdomain_info.tsv").read().splitlines()

subdomainlines = open("final_subdomain_info.tsv").read().splitlines()

num_lines = float(len(subdomainlines))

def reduce_by_tfidf(tfidf_thresh, outf):
	subreddits_by_domain = {}
	for line in tfidflines:
		subdomain, idf, subreddit, tfidf = line.split('\t')
		tfidf = float(tfidf)
		if tfidf >= tfidf_thresh:
			try:
				s = subreddits_by_domain[subdomain]
				s[subreddit] = tfidf
			except KeyError:
				subreddits_by_domain[subdomain] = {subreddit: tfidf}

	out = open(outf, 'w')

	for x, line in enumerate(subdomainlines):
		if x % 100 == 0:
			print x, (x/num_lines)*100, "% done"

		try:
			subdomain, subreddit_str, weight_str = line.split('\t')
		except ValueError:
			print 'bad line:', line 
			continue

		if subdomain in subreddits_by_domain:

			subreddits = subreddit_str.split(',')
			weights = weight_str.split(',')

			for i, subreddit in enumerate(subreddits):
				for j, other in enumerate(subreddits):
					if j > i:
						if subreddit in subreddits_by_domain[subdomain] and other in subreddits_by_domain[subdomain]:
							avg = (float(weights[i]) + float(weights[j])) / 2.0 
							if avg >= weight_threshold:
								out.write(subreddit + '\t' + other + '\t' + str(avg) + '\n')

	out.close()


def reduce_by_idf(idf_thresh, outf):
	allowed_subdomains = set()

	for line in tfidflines:
		subdomain, idf, subreddit, tfidf = line.split('\t')
		if float(idf) >= idf_thresh:
			allowed_subdomains.add(subdomain)

	out = open(outf, 'w')

	for x, line in enumerate(subdomainlines):
		if x % 100 == 0:
			print x, (x/num_lines)*100, "% done"

		try:
			domain, subreddit_str, weight_str = line.split('\t')
		except ValueError:
			print 'bad line:', line 
			continue

		subreddits = subreddit_str.split(',')
		weights = weight_str.split(',')

		for i, subreddit in enumerate(subreddits):
			for j, other in enumerate(subreddits):
				if j > i:
					avg = (float(weights[i]) + float(weights[j])) / 2.0 
					if avg >= weight_threshold:
						out.write(subreddit + '\t' + other + '\t' + str(avg) + '\n')

	out.close()


typ = sys.argv[1]
thresh = sys.argv[2]
outf = sys.argv[3]

if typ == 'idf':
	reduce_by_idf(float(thresh), outf)
elif typ == 'tfidf':
	reduce_by_tfidf(float(thresh), outf)

