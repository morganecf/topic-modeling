"""
This script fills the subreddit_id field 
for wayback submissions by extracting the 
subreddit name from the submission's url. 
"""

# Example: http://www.reddit.com/r/mildlyinteresting/comments/... --> mildlyinteresting
def extract_subreddit(url):
	start = url.find("/r/")
	end = url.find("/", start + 3)
	return url[start + 3:end] 

from redditDB import RedditDB

rdb = RedditDB("mciot", "r3dd1tmorgane", "blacksun.cs.mcgill.ca", 31050, "reddit_topics")

for submission in rdb.get_wayback_submissions():
	url = submission.get("comment_url")
	if url:
		subreddit = extract_subreddit(url)
		subreddit_obj = rdb.subreddit_exists(subreddit)
		# If the subreddit exists and the submission doesn't have an id, update 
		if subreddit_obj and submission.get("subreddit_id") is None:
			rdb.update_wayback_submission(submission.get("_id"), "subreddit_id", subreddit_obj.get("_id"))



