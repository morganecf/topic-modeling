"""
Script to crawl submission content.  
Usage: python scrape.py --topics_file <list of topics> 
						--host blacksun.cs.mcgill.ca 
						--port 31050 
						--username mciot 
						--password passwd 
						--db reddit_topics 
						--limit 900
"""

import argparse
from scraper import Scraper

argparser = argparse.ArgumentParser(description="Scrape Reddit link content.")

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
argparser.add_argument("--limit", help="max number of submissions to update at a time", 
					type=int, default=900)

params = argparser.parse_args()

username = params.username
password = params.password
host = params.host
port = params.port
db = params.db

reddit_agent = "Reddit topics by u/redditTopics"

limit = params.limit

if params.topics_file == "":
	topics_file = None
else:
	topics_file = params.topics_file

puller = Scraper(reddit_agent, username, password, host, port, db)

puller.update_submission_content(topics_file, limit)
