
import utils
import json

# Get subreddit id to name mappings
subreddit_ids = {}
srlines = open("../data/subreddit_to_id.tsv").read().splitlines()
for line in srlines:
	try:
		sr, sid = line.split("\t")
	except ValueError:
		print "Subreddit doesn't have id?", line
		continue
	subreddit_ids[sid] = sr.strip()

xpost_network = {}
subdomains = {}

num_xposts = 0
num_subdomains = 0

counter = 0
log_interval = 50000

# Keep track of praw ids of wayback comments to fetch
wayback_comments = open("../data/wayback_comment_ids.txt", "w")
comment_buffer = []

num_extrapolated = 0
num_not_found = 0
num_found = 0

with open("../mongodump/wayback_submissions.json") as submission_file:
	for submission_raw in submission_file:

		submission = json.loads(submission_raw)

		counter += 1
		if counter % log_interval == 0:
			print "Wayback Progress:", (counter / 18609213.0) * 100, "%"
			print "\tNum unique subdomains:", len(subdomains)
			print "\tNum xposts:", num_xposts
			print "\tNum extrapolated:", num_extrapolated
			print "\tNum subreddit names not found:", num_not_found
			print ""

		# Get praw id and save
		praw_id = submission.get("reddit_id")
		comment_buffer.append(praw_id)
		if len(comment_buffer) >= 100000:
			for pid in comment_buffer:
				wayback_comments.write(str(pid) + '\n')
			comment_buffer = []

		try:
			subreddit_id = str(submission.get("subreddit_id").values()[0])
			subreddit = subreddit_ids[subreddit_id]
			num_found += 1

			title = submission.get("submission_title")
			subdomain = utils.normalize_domain(submission.get("domain"))

			# Get potential xpost info
			xpost = utils.extract_subreddit_xpost(title)
			if not xpost:
				if subdomain and subdomain.startswith("self."):
					internal = subdomain.split(".")[1]
					if internal != subreddit:
						xpost = internal

					subdomain = None

			# Update xpost network
			if xpost:
				edge = (xpost, subreddit)
				try:
					xpost_network[edge] += 1
				except KeyError:
					inverse = (subreddit, xpost)
					try:
						xpost_network[inverse] += 1
					except KeyError:
						xpost_network[edge] = 1

				num_xposts += 1

			# Update subdomains
			if subdomain:
				try:
					s = subdomains[subdomain]
					try:
						s[subreddit] += 1
					except KeyError:
						s[subreddit] = 1
				except KeyError:
					subdomains[subdomain] = {subreddit: 1}

				num_subdomains += 1

		# Attempt to extrapolate domain
		except AttributeError:
			domain = submission.get("domain")
			commenturl = submission.get("comment_url")
			url = submission.get("url")

			# Try looking at praw's domain extraction
			if domain and domain.startswith("self."):
				subreddit = domain.split(".")[1]
				num_extrapolated += 1
			elif domain == "reddit.com" and url:
				subreddit = utils.get_internal_link(url)
				num_extrapolated += 1

			# Otherwise look at comment url for hints
			elif commenturl:
				subreddit = utils.get_internal_link(commenturl)
				num_extrapolated += 1

			else:
				subreddit = None
				num_not_found += 1

			# If domain was found, can't infer subdomain, just try to find
			# xpost in title
			xpost = utils.extract_subreddit_xpost(submission.get("submission_title"))

			if subreddit and xpost:
				subreddit = subreddit.strip()
				xpost = xpost.strip()

				edge = (xpost, subreddit)
				try:
					xpost_network[edge] += 1
				except KeyError:
					inverse = (subreddit, xpost)
					try:
						xpost_network[inverse] += 1
					except KeyError:
						xpost_network[edge] = 1

				num_xposts += 1


wayback_comments.close()

print "Done aggregating from wayback:"
print len(xpost_network), "edges in xpost network"
print len(subdomains), "unique subdomains"
print "Adding current information"

counter = 0
with open("../mongodump/submissions.json") as submission_file:
	for submission_raw in submission_file:

		submission = json.loads(submission_raw)

		try:
			subreddit_id = str(submission.get("subreddit_id").values()[0])
		except AttributeError:
			continue

		subreddit = subreddit_ids[subreddit_id]

		xpost = utils.extract_subreddit_xpost(submission.get("submission_title"))
		url = submission.get("url")
		if url:
			# Check if it's an internal link
			if utils.is_internal(url):
				if xpost is None:
					xpost = utils.get_internal_link(url)
			# Otherwise get external domain name
			else:
				subdomain = utils.get_domain(url)
		else:
			subdomain = None

		# Update xpost network
		# xpost network is directed
		if xpost and xpost != subreddit:
			edge = (subreddit, xpost)
			try:
				xpost_network[edge] += 1
			except KeyError:
				xpost_network[edge] = 1

			num_xposts += 1

		# Update subdomains
		if subdomain:
			try:
				s = subdomains[subdomain]
				try:
					s[subreddit] += 1
				except KeyError:
					s[subreddit] = 1
			except KeyError:
				subdomains[subdomain] = {subreddit: 1}

			num_subdomains += 1

		counter += 1
		if counter % log_interval == 0:
			print "Progress:", (counter / 7333071.0) * 100, "%"
			print "\tNum subdomains:", num_subdomains
			print "\tNum xposts:", num_xposts
			print ""

print "Done aggregating from wayback:"
print len(xpost_network), "edges in xpost network"
print len(subdomains), "unique subdomains"
print "Adding current information"

# Save xpost network
xpostf = open('../data/networks/final_xpost_network.tsv', 'w')

for edge, weight in xpost_network.iteritems():
	xpostf.write(edge[0] + '\t' + edge[1] + '\t' + str(weight) + '\n')

xpostf.close()

# Save subdomain information
subdomainf = open('../data/networks/final_subdomain_info.tsv', 'w')

for subdomain, subreddit_dict in subdomains.iteritems():
	subreddits = subreddit_dict.keys()
	weights = map(lambda srd: str(subreddit_dict[srd]), subreddits)
	subreddit_str = ','.join(subreddits).encode("utf8")
	weight_str = ','.join(weights).encode("utf8")
	subdomain = subdomain.encode("utf8")
	subdomainf.write(subdomain + '\t' + subreddit_str + '\t' + weight_str + '\n')

subdomainf.close()