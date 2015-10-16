""" 
Scrapes wayback submissions 
Usage: python scrape_wayback_submissions.py username password year limit
Where username and password are your blacksun mongodb credentials
year is the year you want to scrape (ex: 2012)
limit is the number of snapshots per day you want to get (ex: a maximum of 4)
"""

# TODO This needs to be multithreaded or distributed 

import sys
from conf_scraper import Conf
import redditDB as rdb
from wayback import scrape_submissions

confFile = raw_input('conf_file: ')
params = Conf(confFile)
username = params.username
password = params.password
host = params.host
port = params.port
dbase = params.db
reddit_agent = "Reddit topics by u/redditTopics"
year = raw_input('year: ')

try:
	#username = sys.argv[2]
	#password = sys.argv[3]
	#year = sys.argv[1]
	snapshot_limit = 900
except IndexError:
	print "Usage: python scrape_wayback_submissions.py  <year> <optional filename of topics>"
	sys.exit(0)

user_agent = {"User-agent": "reddit_topics v1"}

url2008 = "http://web.archive.org/web/20080615000000*/http://reddit.com/r/"
url2009 = "http://web.archive.org/web/20090715000000*/http://reddit.com/r/"
url2010 = "http://web.archive.org/web/20100601000000*/http://reddit.com/r/"
url2011 = "http://web.archive.org/web/20110501000000*/http://reddit.com/r/"
url2012 = "http://web.archive.org/web/20120415000000*/http://reddit.com/r/"
url2013 = "http://web.archive.org/web/20130515000000*/http://reddit.com/r/"
url2014 = "http://web.archive.org/web/*/http://reddit.com/r/"

years = {"2013": url2013, "2012": url2012, "2014": url2014, "2011": url2011, "2010": url2010, "2009": url2009, "2008": url2008}

try:
	yr = years[year]
except KeyError:
	print "Year not available."
	sys.exit(0)

db = rdb.RedditDB(username, password, host, port, dbase)

try:
	filename = params.topics_file
	topics = open(filename).read().splitlines()
	subreddits = db.get_subreddits(topics=topics)
except IndexError:
	subreddits = db.get_subreddits()
except IOError:
	print "Cannot find topics file."
	sys.exit(0)
 
for subreddit in subreddits:
	x = subreddit.get("subreddit_name")
	print x
	scrape_submissions(yr, subreddit, snapshot_limit, db, user_agent)

