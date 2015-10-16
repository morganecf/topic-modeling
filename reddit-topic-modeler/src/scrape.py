"""
Script for a node to get data from reddit. 
Usage: python scrape.py --topics_file <list of topics> 
						--host blacksun.cs.mcgill.ca 
						--port 31050 
						--username mciot 
						--password passwd 
						--db reddit_topics 
						--sleep 3600 
						--limit 900
						--links
"""
#import create_conf_file
#from conf_scraper import Conf

import argparse
from scraper import Scraper

argparser = argparse.ArgumentParser(description="Pull data from Reddit.")

argparser.add_argument("--topics_file",
					help="path to the file of topics you want to update",
					default=None)
argparser.add_argument("--reddit_agent",  
					help="Praw reddit agent name-can be anything",
					default="Reddit topics by u/redditTopics")
argparser.add_argument("--db", help="mongo database name", default="reddit_topics")
argparser.add_argument("--host", help="mongodb host", default="blacksun.cs.mcgill.ca")
argparser.add_argument("--port", help="mongodb port", default=31050)
argparser.add_argument("--username", help="mongodb username")
argparser.add_argument("--password", help="mongodb password")
argparser.add_argument("--sleep", help="seconds to sleep before pulling data again", 
					type=int, default=3600)
argparser.add_argument("--limit", help="max number of submissions to get in each pull (limit 1000)", 
					type=int, default=900)

# This is kind of bad since argparser isn't supposed to be used for flags,
# just arguments :/
argparser.add_argument("--links", help="use true to scrape link content", default=False)

params = argparser.parse_args()

#confFile = raw_input('conf_file: ')
# confFile = create_conf_file.create()
# params = Conf(confFile)

username = params.username
password = params.password
host = params.host
port = params.port
db = params.db

reddit_agent = "Reddit topics by u/redditTopics"

# sleep = 3600
# limit = 900

sleep = params.sleep
limit = params.limit
links = True if params.links == "true" else False 

if params.topics_file == "":
	topics_file = None
else:
	topics_file = params.topics_file

puller = Scraper(reddit_agent, username, password, host, port, db)

puller.update_submissions(topics_file, hot_sleep=sleep, submission_limit=limit, follow_links=links)
