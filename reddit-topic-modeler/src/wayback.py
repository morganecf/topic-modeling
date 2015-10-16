import bs4
import time
import urllib2 
from datetime import datetime

# TODO: Switch to httplib or Requests to speed up

# TODO: Can scrape front page snapshots from reddit.com (no /r/) since 2005
# but might have different format 
# Also these only include the default subreddits 
# So could be easier to scrape because only doing like 8 of them 
# April 10th 2008: start of subreddits 

# TODO: Scrape content from url of submission? 

months = {
	"01" : "Jan",
	"02" : "Feb",
	"03" : "Mar",
	"04" : "Apr",
	"05" : "May",
	"06" : "Jun",
	"07" : "Jul",
	"08" : "Aug",
	"09" : "Sep",
	"10" : "Oct",
	"11" : "Nov",
	"12" : "Dec"
}

def pad(date):
	dateinfo = date.split()
	if len(dateinfo[1]) == 1:
		dateinfo[1] = "0"+dateinfo[1]
	return ' '.join(dateinfo)

def to_timestamp(div):
	try:
		# Should be in following format: Jan 2 02:57:13 2013
		timestamp = " ".join(div.find("time").get("title").split()[1:-1])

		# ?? 
		if len(timestamp.split()) != 4:
			print "faulty timestamp?", timestamp
			timestamp = ' '.join(div.find("time").get("datetime").split('T'))

		try:
			return datetime.strptime(timestamp, "%b %d %H:%M:%S %Y")
		except ValueError:
			print "New date created format:", timestamp
			return timestamp
	except AttributeError:
		return None
	except ValueError:
		return None

def is_submission_class(cssclass):
	try:
		classes = cssclass.get("class")
		return " thing id-" in ' '.join(classes)
		#return ' '.join(classes).strip().startswith("thing id-")
	except TypeError:
		return False

def is_comment_class(cssclass):
	try:
		classes = cssclass.get("class")
		name = ' '.join(classes).strip()
		return name.startswith("thing id-") and name.endswith("comment")
	except TypeError:
		return False

def find_submission_text(divs):
	for div in divs:
		# must be first 
		if is_submission_class(div):
			try:
				return div.find("form", "usertext").text
			except AttributeError:
				return ""

def getChildren(comment):
	divs = comment.find_all("div")
	return filter(is_comment_class, divs)

def layer_helper(comments, layers, layernum, offset):
	for x in range(0, len(comments)):
		index = x + offset
		if not layers[index]:
			layers[index] = layernum
			sub = getChildren(comments[x])
			if sub:
				layer_helper(sub, layers, layernum + 1, x + offset + 1)
				next = len(sub) + x + 1
				x = next 

def layer(comments):
	layers = [0]*len(comments)
	layer_helper(comments, layers, 1, 0)
	return layers 


def snapshot_link(snap_html):
	return "http://web.archive.org" + snap_html.find("a").get("href")

''' 
Scrapes comments for a submission 
TODO: exception handling. but try running first to see if structure has changed 
'''
def scrape_comments(submission, db, user_agent):
	# If comments were already scraped don't need to do anything
	if submission.get("hasComments"):
		return

	# Otherwise follow link to comments if possible 
	reddit_link = submission.get("comment_url")
	if not reddit_link:
		return

	reddit_id = submission.get("reddit_id") 	# alternatively: reddit_link.split('/')[6]	
	submission_id = submission.get("_id")
	try:
		comment_req = urllib2.Request(url=reddit_link, headers=user_agent)
		comment_html = urllib2.urlopen(comment_req).read()
	except urllib2.URLError as e:
		print "URLError:", e.strerror
		db.log("URLError-comment", submission_id)
		return

	comment_soup = bs4.BeautifulSoup(comment_html)
	
	# Get top 200 comments (would have to follow another link to get more)
	comment_divs = comment_soup.find_all("div")		
	comments = filter(is_comment_class, comment_divs)
	
	# Recursively assign layer to each one 
	layers = layer(comments)

	# Now update submission's text field 
	submission_text = find_submission_text(comment_soup.find_all("div"))
	db.submission_collection.update( {"_id": submission_id}, {"submission_text": submission_text} )

	# Add all comments 
	for index, comment in enumerate(comments):
		comment_text = comment.find("form", "usertext").text
		upvotes = int(comment.find("span", "likes").text.split()[0])
		downvotes = int(comment.find("span", "dislikes").text.split()[0])
		layernum = layers[index]

		created = to_timestamp(comment)
		comment_doc = {"comment_text": comment_text,
					"karma": upvotes,
					"downvotes": downvotes,
					"layer": layernum,
					"submission_id": submission_id,
					"topic_id": submission.get("subreddit_id"),
					"created": created,
					"reddit_id": reddit_id }
		comment_id = db.insert_wayback_comment(comment_doc)
		# If successfully inserted set hasComments to true
		if comment_id:
			db.submission_collection.update({"_id": submission_id}, {"hasComments": True}, timeout=False)

''' 
Scrapes submissions for a subreddit (without comments) 
snap_limit indicates the number of snapshots to scrape 
Set try_failed to True if want to try scraping snapshots 
that previously failed. 
''' 
def scrape_submissions(base_url, subreddit, snap_limit, db, user_agent, try_failed=False):

	start = time.time()

	subreddit_id = subreddit.get("id")
	name = subreddit.get("subreddit_name")
	snapshots = db.get_snapshots(subreddit_id)

	# If doesn't already exist, need to get them for first time 
	if snapshots is None:
		url = base_url + name 
		# Open subreddit page if possible
		try:
			req = urllib2.Request(url, headers=user_agent)
		except urllib2.URLError:
		 	db.log("URLError-subreddit", subreddit_id)
		 	return
		try:
			html = urllib2.urlopen(req).read()
		except urllib2.HTTPError:
			return
		soup = bs4.BeautifulSoup(html)

		# Each pop is a day that was snapshotted 
		pops = soup.find_all("div", "pop")

		# Save snapshots that aren't explored now to explore for later 
		total_missing_snapshots = []
		# Save snapshots whose pages fail to open (can maybe try again)
		total_failed_snapshots = []

		for pop in pops:

			# Each snap is a specific snapshot within that day 
			snapshots = pop.find_all("li")
			num_snapshots = len(snapshots)

			missing_snapshots = []
			failed_snapshots = []

			# Limit ones to explore now to num_snaps 
			if snap_limit < num_snapshots: 
				snapshots_copy = snapshots[:]
				snapshots = snapshots_copy[:snap_limit]
				missing_snapshots.extend([snapshot_link(snap) for snap in snapshots_copy[snap_limit:]])
				num_snapshots = snap_limit

			for snap in snapshots:
				# Returns the number of submissions it got 
				scraped = scrape_snapshot(snapshot_link(snap), subreddit_id, db, user_agent)
				# If didn't manage to scrape any add to failed list
				if not scraped: 
					failed_snapshots.append(snapshot_link(snap))

			# Each entry essentially corresponds to a day 
			total_missing_snapshots.append(missing_snapshots)
			total_failed_snapshots.append(failed_snapshots)

		# Add missing/failed list of lists to subreddit 
		db.subreddit_collection.update({"_id": subreddit_id}, {"missing_snapshots":total_missing_snapshots})
		db.subreddit_collection.update({"_id": subreddit_id}, {"failed_snapshots":total_failed_snapshots})

	# Otherwise scrape the snapshots that are leftover from last time
	# Format is list of lists, each list indicating a day (pop)
	elif len(snapshots) > 0:
		for i, day in enumerate(snapshots): 
			# Only do up to snap_limit
			day_snaps = day[:]
			for snap in day[:snap_limit]:
				scraped = scrape_snapshot(snap, subreddit_id, db, user_agent)
				# If successfully scraped, update list copy 
				if scraped: 
					day_snaps.remove(snap)
			snapshots[i] = day_snaps
		db.subreddit_collection.update({"_id":subreddit_id}, {"missing_snapshots":snapshots})

	# If user wants to try previously failed snapshots, get these
	if try_failed:
		failed = db.get_failed_snapshots(subreddit_id)
		if failed:
			for i,day in enumerate(failed): 
				day_snaps = day[:]
				# Only do up to snap_limit 
				for snap in day[:snap_limit]:
					scraped = scrape_snapshot(snap, subreddit_id, db, user_agent)
					# If successfully scraped, update list copy
					if scraped:
						day_snaps.remove(snap)
				failed[i] = day_snaps
			db.subreddit_collection.update({"_id":subreddit_id}, {"failed_snapshots":failed})

	print "\t", time.time() - start 


''' Scrapes submissions for a subreddit without comments ''' 
def scrape_snapshot(snaplink, subreddit_id, db, user_agent):
	snap_req = urllib2.Request(url=snaplink, headers=user_agent)
	num_submissions = 0
	try:
		snap_html = urllib2.urlopen(snap_req).read()
		snap_soup = bs4.BeautifulSoup(snap_html)
		divs = snap_soup.find_all("div")
		submissions = filter(is_submission_class, divs)
		
		for submission in submissions:
			classes = submission.get("class")
			try:
				reddit_id = classes[2].split("_")[1]    # TODO: Does this always work? 
			except IndexError:
				for x in range(len(classes)):
				        y = classes[x].split('_')
				        if len(y) > 1:
				                reddit_id = y[1]

			try:
				upvotes = submission.find("div", class_="score likes").text
			except ValueError:
				upvotes = 0
			except AttributeError:
				upvotes = 0
			try:
				downvotes = submission.find("div", class_="score dislikes").text
			except ValueError:
				downvotes = 0
			except AttributeError:
				downvotes = 0 
			try:
				title = submission.find("a", class_="title").text 	
			except AttributeError: 
				title = ""
			# Get the link to actual content (can potentially scrape this later)
			try:
				title_link = submission.find("a", class_="title").get("href")
				start_index = title_link.find("http")
				submission_url = title_link[start_index:]
			except AttributeError:
				submission_url = None
			try:
				num_comments = int(submission.find("a", class_="comments").text.split()[0].strip())
			except ValueError:
				num_comments = 0
			except AttributeError:
				num_comments = 0
			try:
				domain = submission.find("span", class_="domain").text.replace("(", "").replace(")", "")
			except AttributeError:
				domain = None
			# Date submission was created
			timestamp = to_timestamp(submission)
			# Get direct reddit link to comments 
			try:
				wayback_link = submission.find("a", class_="comments").get("href")
				start_index = wayback_link.find("http")
				reddit_link = wayback_link[start_index:]
			except AttributeError:
				reddit_link = None

			# Construct mongodb document 
			submission_doc = { "subreddit_id": subreddit_id,
							"submission_title": title,
							"karma": upvotes,
							"downvotes": downvotes,
							"num_comments": num_comments,
							"domain": domain,
							"url": submission_url,
							"created": timestamp,
							"comment_url": reddit_link,
							"reddit_id": reddit_id,
							"hasComments": False }
		
			# Add doc to mongodb 
			db.insert_wayback_submission(submission_doc)
			num_submissions += 1
		return num_submissions
	# If opening snapshot failed, scraped 0 submissions
	except urllib2.URLError:
		return 0

# num_days = 0
# 		total_snapshots = 0
# 		total_failed_snapshots = 0
# 		total_submissions = 0
# 	popdate = pop.find("h3").text
# #		print "\t"+popdate+", "+str(num_submissions)+" submissions from "+str(num_snapshots-num_failed)+" snapshots"
# 	num_days += 1
# 	total_submissions += num_submissions
# 	total_snapshots += num_snapshots 
# 	total_failed_snapshots += num_failed 
# 	# Log only if all snapshots failed (then we have nothing for that day)
# 	if num_failed == num_snapshots: 
# #			print "\tNo snapshots from ", popdate
# 		errstr = str(subreddit_id) + "-" + name + "-" + popdate
# 		db.log("URLError-snapshot", errstr)
# 	# Save missing links in database 
# 	db.subreddit_collection.update({"_id": subreddit_id}, {"missing_snapshots": missing_snapshots})

# 	t2 = time.time()
# 	elapsed = t2-t1
# 	minutes = elapsed/60.0
# 	print "\t"+str(total_submissions)+" submissions from "+str(num_days)+" days"
# 	print "\t"+str(total_snapshots-total_failed_snapshots)+"/"+str(total_snapshots)+" snapshots successfully reached"
# 	print "\tTotal time taken: "+str(minutes)+" minutes"


# # datetime.fromtimestamp(1385684456)
