"""
Crawl Reddit's related subreddits sections to build network
of interrelated subreddits based on reddit's recommendations.

Usage: python crawl_related_subreddits.py <subreddit list>
"""

import sys
import time
import socket
import httplib
import urllib2
from bs4 import BeautifulSoup as bs

user_agent = {'user-agent': 'my related'}
clear_interval = 100

# Save ones where error may have occurred
unexplored = open("../data/networks/unexplored_subreddits.txt", "w")

# Keep track of what's been done
log = open("../data/networks/related_subreddits_log.txt", "w")

def is_related_subreddit(a):
	return 'href' in a.attrs and '/r/' in a.attrs['href'] and len(a.attrs['href'].split('/r/')[1].split('/')) <= 1

def get_related(subreddit, edges, seen):
	if subreddit in seen:
		return
	else:
		seen[subreddit] = 1

	url = "http://www.reddit.com/r/" + subreddit

	try:
		req = urllib2.Request(url, headers=user_agent)
		try:
			html = urllib2.urlopen(req).read()
			soup = bs(html)
			try:
				div = soup.find("div", "side").find("div", "usertext-body may-blank-within md-container")
				atags = div.find_all('a')
				related = []
				for at in atags:
					if is_related_subreddit(at):
						sr = at.attrs['href'].split('/r/')[1].strip()
						if '+' in sr:
							srs = sr.split('+')
							for _sr in srs:
								if _sr != subreddit:
									edges.append((subreddit, _sr))
									#print "\t", _sr
									related.append(_sr)
						else:
							if sr != subreddit:
								edges.append((subreddit, sr))
								#print "\t", sr
								related.append(sr)
				return related
			except AttributeError:
				print 'No side div found for::::', subreddit
				unexplored.write(subreddit + "\n")
				unexplored.flush()
		except httplib.IncompleteRead:
			print 'Incomplete read for::::', subreddit
			unexplored.write(subreddit + "\n")
			unexplored.flush()
		except urllib2.HTTPError:
			print 'HTTPError on::::', subreddit
			unexplored.write(subreddit + "\n")
			unexplored.flush()
	except urllib2.URLError:
		print 'URLError on::::', subreddit
		unexplored.write(subreddit + "\n")
		unexplored.flush()
	except socket.error:
		print 'SocketError on::::', subreddit
		unexplored.write(subreddit + "\n")
		unexplored.flush()
		time.sleep(5)


def clear(edges, out):
	print "Clearing edge buffer..."
	for edge in edges:
		out.write("\t".join([edge[0], edge[1]]) + "\n")
	out.flush()

	children = map(lambda e: e[1], edges)
	edges = []

	print "Exploring", len(children), "children"
	for child in children:
		rel = get_related(child, edges, seen)
		if rel is not None:
			print child, ":", len(rel), "related;;", len(edges), "edges;; ", len(seen), "nodes"

	return edges

def crawl_network(subreddits, out, edges, seen, num_edges):
	for i, subreddit in enumerate(subreddits):

		rel = get_related(subreddit, edges, seen)
		if rel is not None:
			print subreddit, ":", len(rel), "related;;", len(edges), "edges;; ", len(seen), "nodes"

		# At set intervals, clear edge buffer to file
		# and start crawl from newer nodes
		if len(edges) >= clear_interval:
			num_edges += len(edges)
			s1 = str(len(seen)) + " nodes (unique subreddits)\n"
			s2 = str(num_edges) + " edges\n"
			s3 = "Gone through " + str(i + 1) + " out of " + str(len(subreddits)) + " input subreddits\n"
			print "\n========================"
			print s1, s2, s3
			print("========================\n")
			log.write(s1)
			log.write(s2)
			log.write(s3)
			log.write("\n")
			log.flush()
			edges = clear(edges, out)


	# When done, make sure to clear everything and
	# continue getting edges
	print "Done going through input list, expanding on rest of subreddits..."
	while len(edges) > 0:
		num_edges += len(edges)
		s1 = str(len(seen)) + " nodes (unique subreddits)\n"
		s2 = str(num_edges) + " edges\n"
		print "\n========================"
		print s1, s2
		print("========================\n")
		log.write(s1)
		log.write(s2)
		log.write("\n")
		log.flush()
		edges = clear(edges, out)

f = open("../data/networks/related_edges.tsv", "w")
l = open(sys.argv[1]).read().splitlines()

num_edges = 0
edges = []
seen = {}

crawl_network(l, f, edges, seen, num_edges)

f.close()
log.close()
unexplored.close()

print "Done crawling all", len(l), "input subreddits and their associated subreddits!"
