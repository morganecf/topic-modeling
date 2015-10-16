'''
Methods to build subreddit networks based on new text-based
directory structure.
'''

import os
import math
from datetime import datetime

'''
TF-IDF strategy:
document = subreddit

TF = term frequency = how often a url appears in a subreddit
TF(url) = number of times url appears in subreddit / total number of urls in subreddit

IDF = inverse document frequency = how important a url is
IDF(url) = ln(total number of subreddits / number of subreddits containing url)
'''

base_dir = os.path.join("..", "data", "reddit")

def non_user_networks():
	num_subreddits = 0

	# Format: {domain:{subreddit:int}}
	domains = {}

	# Used for tf-idf
	num_urls_per_subreddit = {}

	# Format: {(subreddit1, subreddit2):int}
	# COMBINED SUBDOMAINS + XPOSTS
	xposts= {}

	print "Aggregating information..."

	# Aggregate information from files across all subdirectories
	trie = filter(lambda d: len(d) == 1, os.listdir(base_dir))
	for branch in trie:
		print branch
		branch_path = os.path.join(base_dir, branch)
		for subreddit in os.listdir(branch_path):
			print '\t', subreddit
			subreddit_path = os.path.join(branch_path, subreddit)
			num_subreddits += 1
			for year in os.listdir(subreddit_path):
				year_path = os.path.join(subreddit_path, year)
				for month in os.listdir(year_path):
					month_path = os.path.join(year_path, month)
					for day in os.listdir(month_path):
						day_path = os.path.join(month_path, day)

						# Take care of domain stuff
						try:
							domain_lines = open(os.path.join(day_path, 'domains.txt')).read().splitlines()
						except IOError:
							continue

						for i, line in enumerate(domain_lines):
							try:
								domain = line.split('\t')[1]
							except IndexError:
								continue

							# Found cross-post (internal subdomain)
							if domain.startswith("self."):
								other = domain.split("self.")[1]
								if other != subreddit:
									pair = (subreddit, other)
									try:
										xposts[pair] += 1
									except KeyError:
										inverse_pair = (other, subreddit)
										try:
											xposts[inverse_pair] += 1
										except KeyError:
											xposts[pair] = 1

							# Otherwise, regular subdomain
							else:
								try:
									d = domains[domain]
									try:
										d[subreddit] += 1
									except KeyError:
										d[subreddit] = 1
								except KeyError:
									domains[domain] = {subreddit: 1}

						# Aggregate number of urls posted in this subreddit
						try:
							num_urls_per_subreddit[subreddit] += len(domain_lines)
						except:
							num_urls_per_subreddit[subreddit] = len(domain_lines)

						# Take care of xpost stuff
						try:
							xpost_lines = open(os.path.join(day_path, 'xposts.txt')).read().splitlines()
						except IOError:
							continue

						# Combine xposts with subdomains
						for line in xpost_lines:
							xpost = line.split('\t')[1]
							if xpost != subreddit:
								pair = (xpost, subreddit)
								try:
									xposts[pair] += 1
								except KeyError:
									try:
										inverse_pair = (subreddit, xpost)
										xposts[inverse_pair] += 1
									except KeyError:
										xposts[pair] = 1


	print "Done aggregating."
	info_str = str(num_subreddits) + ' subreddits\n' + str(len(xposts)) + ' xpost edges\n'
	info_str += str(len(domains)) + ' urls total\n'
	print info_str

	# We now have the xpost network
	# Save it to a file.
	timestamp = '_'.join(''.join(str(datetime.today()).split('.')[:-1]).split())
	save_path = '../data/networks/networks/' + timestamp + '/'

	os.system("mkdir " + save_path)

	print 'Saving in:', timestamp

	# File format: subreddit1 \t subreddit2 \t weight
	xpost_file = open(save_path + 'xpost_network.tsv', 'w')

	print 'Saving xpost network'
	for pair, weight in xposts.iteritems():
		xpost_file.write(pair[0] + '\t' + pair[1] + '\t' + str(weight) + '\n')

	xpost_file.close()

	# Create domain network and gather domain tf-idf stats
	domain_network = {}

	# File format: first line: total_num_subreddits
	# domain \t idf,num_subreddits_having_domain \t sr1,num_times_url_in_subreddit,total_urls_in_subreddit,tf1,tf-idf1 \t...etc
	domain_info_file = open(save_path + 'domain_info.txt', 'w')

	# Stores all possible edges and the domain that caused there to be an edge
	# Format: domain \t subreddit1 \t subreddit2 \t num_times_domain_in_s1 \t num_times_domain_in_s2
	domain_edges = open(save_path + 'domain_edges.txt', 'w')

	print 'Aggregating domain information and saving domain tf-idf stats...'

	num_total_domain_edges = 0

	for domain, subreddits in domains.iteritems():
		# Calculate domain's idf score
		idf = math.log(float(num_subreddits) / float(len(subreddits)))

		line = domain + '\t' + str(len(subreddits)) + ',' + str(idf) + '\t'

		for subreddit, count in subreddits.iteritems():
			# Calculate tf-idf score
			tf = float(count) / float(num_urls_per_subreddit[subreddit])
			tf_idf = tf * idf

			line_info = ','.join([subreddit, str(count), str(num_urls_per_subreddit[subreddit]), str(tf), str(tf_idf)])
			line += line_info + '\t'

		domain_info_file.write(line + '\n')

		# Now add to the network
		srs = subreddits.keys()
		for i, subreddit1 in enumerate(srs):
			for j, subreddit2 in enumerate(srs):
				if j > i:
					# Write edge info
					s = '\t'.join([domain, subreddit1, subreddit2, str(subreddits[subreddit1]), str(subreddits[subreddit2])])
					domain_edges.write(s + '\n')
					num_total_domain_edges += 1

					# Update network
					pair = (subreddit1, subreddit2)
					try:
						domain_network[pair] += 1
					except KeyError:
						inverse_pair = (subreddit2, subreddit1)
						try:
							domain_network[inverse_pair] += 1
						except KeyError:
							domain_network[pair] = 1

	domain_edges.close()
	domain_info_file.close()

	info_str += str(num_total_domain_edges) + ' total unaggregated domain edges\n'
	info_str += str(len(domain_network)) + ' aggregated domain edges\n'

	# This will store the raw network without taking into account tf-idf score
	# Format: subreddit1 \t subreddit2 \t weight
	domain_file = open(save_path + 'domain_network_raw.tsv', 'w')

	print 'Saving raw domain network'
	for pair, weight in domain_network.iteritems():
		domain_file.write(pair[0] + '\t' + pair[1] + '\t' + str(weight) + '\n')

	domain_file.close()

	print info_str

	infofile = open(save_path + 'info.txt', 'w')
	infofile.write(info_str)
	infofile.close()


def user_networks():
	print "Aggregating user information..."

	# Now take care of user networks (comments, submissions, both)
	users = {}		# Format: {username:{subreddit:count, subreddit:count ...}...}
	user_submissions = {}
	user_comments = {}
	submission_lines = open(os.path.join(base_dir, 'users', 'submissions.txt')).read().splitlines()
	comment_lines = open(os.path.join(base_dir, 'users', 'comments.txt')).read().splitlines()

	def aggregate(d, name, subreddit, count):
		try:
			u = d[name]
			ut = users[name]
			try:
				u[subreddit] += count
				ut[subreddit] += count
			except KeyError:
				u[subreddit] = count
				ut[subreddit] = count
		except KeyError:
			d[name] = {subreddit: count}
			users[name] = {subreddit: count}

	for line in submission_lines:
		name, uid, subreddit, count = line.split('\t')
		try:
			count = int(count)
			aggregate(user_submissions, name, subreddit, count)
		except ValueError:
			try:
				count = int(float(count))
				aggregate(user_submissions, name, subreddit, count)
			except ValueError:
				# This means get a $ and count is actually {subreddit:count} dict
				info = count.split(', ')
				for rawpair in info:
					pair = rawpair.split(':')
					subreddit = pair[0].replace("{u'", '').replace("'", "")
					count = int(pair[1].strip().replace("}", ""))
					aggregate(user_submissions, name, subreddit, count)


	for line in comment_lines:
		name, uid, subreddit, count = line.split('\t')
		try:
			count = int(count)
			aggregate(user_comments, name, subreddit, count)
		except ValueError:
			try:
				count = int(float(count))
				aggregate(user_comments, name, subreddit, count)
			except ValueError:
				# This means get a $ and count is actually {subreddit:count} dict
				info = count.split()
				for rawpair in info:
					pair = rawpair.split(':')
					subreddit = pair[0].replace("{u'", '').replace("'", "")
					count = int(pair[1].strip().replace("}", ""))
					aggregate(user_comments, name, subreddit, count)


	info_str = str(len(user_submissions)) + ' users with submission activity\n'
	info_str += str(len(user_comments)) + ' users with comment activity\n'
	info_str += str(len(users)) + ' total users\n'

	print info_str

	print "Building user networks..."

	log_interval = 100

	submission_network = {}
	comment_network = {}
	user_network = {}

	# Create networks with two types of weights -
	# weighted by AVERAGE user activity ACROSS BOTH SUBREDDITS, and unweighted

	print "Building submission network..."

	counter = 0
	# Create submission network
	for user, subreddits in user_submissions.iteritems():
		srs = subreddits.keys()
		for i, subreddit1 in enumerate(srs):
			for j, subreddit2 in enumerate(srs):
				if j > i:
					pair = (subreddit1, subreddit2)
					avg_weight = (subreddits[subreddit1] + subreddits[subreddit2]) / 2
					try:
						submission_network[pair]['unweighted'] += 1
						submission_network[pair]['weighted'] += avg_weight
					except KeyError:
						inverse_pair = (subreddit2, subreddit1)
						try:
							submission_network[inverse_pair]['unweighted'] += 1
							submission_network[inverse_pair]['weighted'] += avg_weight
						except KeyError:
							submission_network[pair] = {'unweighted': 1, 'weighted': avg_weight}

		if counter % log_interval == 0:
			print "Submission network progress::", (counter / float(len(user_submissions))) * 100, "%"
		counter += 1

	print "Building comment network..."

	counter = 0
	# Create comment network
	for user, subreddits in user_comments.iteritems():
		srs = subreddits.keys()
		for i, subreddit1 in enumerate(srs):
			for j, subreddit2 in enumerate(srs):
				if j > i:
					pair = (subreddit1, subreddit2)
					avg_weight = (subreddits[subreddit1] + subreddits[subreddit2]) / 2
					try:
						comment_network[pair]['unweighted'] += 1
						submission_network[pair]['weighted'] += avg_weight
					except KeyError:
						inverse_pair = (subreddit2, subreddit1)
						try:
							comment_network[inverse_pair]['unweighted'] += 1
							comment_network[inverse_pair]['weighted'] += avg_weight
						except KeyError:
							comment_network[pair] = {'unweighted': 1, 'weighted': avg_weight}

		if counter % log_interval == 0:
			print "Comment network progress::", (counter / float(len(user_comments))) * 100, "%"
		counter += 1

	print "Building total user network..."

	counter = 0
	# Create total network
	for user, subreddits in users.iteritems():
		srs = subreddits.keys()
		for i, subreddit1 in enumerate(srs):
			for j, subreddit2 in enumerate(srs):
				if j > i:
					pair = (subreddit1, subreddit2)
					avg_weight = (subreddits[subreddit1] + subreddits[subreddit2]) / 2
					try:
						user_network[pair]['unweighted'] += 1
						user_network[pair]['weighted'] += avg_weight
					except KeyError:
						inverse_pair = (subreddit2, subreddit1)
						try:
							user_network[inverse_pair]['unweighted'] += 1
							user_network[inverse_pair]['weighted'] += avg_weight
						except KeyError:
							user_network[pair] = {'unweighted': 1, 'weighted': avg_weight}

		if counter % log_interval == 0:
			print "Total user network progress::", (counter / float(len(users))) * 100, "%"
		counter += 1

	info_str += str(len(submission_network)) + ' edges in submission user network\n'
	info_str += str(len(comment_network)) + ' edges in comment user network\n'
	info_str += str(len(user_network)) + ' edges in total user network\n'

	print info_str

	# Save networks
	timestamp = '_'.join(''.join(str(datetime.today()).split('.')[:-1]).split())
	save_path = '../data/networks/user/' + timestamp + '/'
	os.system("mkdir " + save_path)

	# Submission users

	# Submission user + weighted
	sw = open(save_path + 'submission_weighted.tsv', 'w')

	# Submission user + unweighted
	su = open(save_path + 'submission_unweighted.tsv', 'w')

	for pair, scheme in submission_network.iteritems():
		sw.write(pair[0] + '\t' + pair[1] + '\t' + str(scheme['weighted']) + '\n')
		su.write(pair[0] + '\t' + pair[1] + '\t' + str(scheme['unweighted']) + '\n')

	sw.close()
	su.close()

	# Comment users

	# Comment user + weighted
	cw = open(save_path + 'comment_weighted.tsv', 'w')

	# Comment user + unweighted
	cu = open(save_path + 'comment_unweighted.tsv', 'w')

	for pair, scheme in comment_network.iteritems():
		cw.write(pair[0] + '\t' + pair[1] + '\t' + str(scheme['weighted']) + '\n')
		cu.write(pair[0] + '\t' + pair[1] + '\t' + str(scheme['unweighted']) + '\n')

	cw.close()
	cu.close()

	# Total user networks

	# Total user + weighted
	tw = open(save_path + 'user_weighted.tsv', 'w')

	# Total user + unweighted
	tu = open(save_path + 'user_unweighted.tsv', 'w')

	for pair, scheme in user_network.iteritems():
		tw.write(pair[0] + '\t' + pair[1] + '\t' + str(scheme['weighted']) + '\n')
		tu.write(pair[0] + '\t' + pair[1] + '\t' + str(scheme['unweighted']) + '\n')

	tw.close()
	tu.close()

	infofile = open(save_path + 'info.txt', 'w')
	infofile.write(info_str)
	infofile.close()

user_networks()