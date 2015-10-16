""" Scrapes wayback machine comments """ 

# TODO This needs to be multithreaded or distributed 
import argparse
import redditDB as rdb
from wayback import scrape_comments

argparser = argparse.ArgumentParser(description="Pull data from Reddit.")

argparser.add_argument("--topics_file", help="path to the file of topics you want to update", default=None)
argparser.add_argument("--db", help="mongo database name", default="reddit_topics")
argparser.add_argument("--host", help="mongodb host", default="blacksun.cs.mcgill.ca")
argparser.add_argument("--port", help="mongodb port", default=31050)
argparser.add_argument("--username", help="mongodb username")
argparser.add_argument("--password", help="mongodb password")

params = argparser.parse_args()

username = params.username
password = params.password
host = params.host
port = params.port
database = params.db
reddit_agent = "Reddit topics by u/redditTopics"

user_agent = {"User-agent": reddit_agent}

db = rdb.RedditDB(username, password, host, port, database)

counter = 0

submissions = db.wayback_submission_list()
for submission in submissions:
	counter += 1
	if counter % 10000 == 0:
		print counter
	scrape_comments(submission, db, user_agent)
