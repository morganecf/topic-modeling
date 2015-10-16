# 1) # of posts
# 2) # of comments per post
# 3) # of words/post
# 4) # of words 
# 5) % of posts with links
# 6) % of posts with image links 
# 7) % of posts with only image links and little text < 20 chars 

import redditDB as rdb 
from utils import get_domain

img_extensions = open("../data/img_extensions.txt").read().splitlines()
img_sharers = open("../data/img_sharers.txt").read().splitlines()

def is_image_link(url):
	if url.split('.')[-1] in img_extensions:
		return True 
	domain = get_domain(url).split('.')
	for sharer in img_sharers:
		if sharer in domain: 
			return True 
	return False 

def is_video(url):
	domain = get_domain(url).split('.')
	for sharer in ['youtube', 'vimeo']:
		if sharer in domain:
			return True 
	return False 

db = rdb.RedditDB('mciot', 'r3dd1tmorgane')

stats = {}

subreddits = db.get_subreddits()

for subreddit in subreddits:
	print subreddit.get("subreddit_name")

	num_comments = 0
	num_post_words = 0
	num_comment_words = 0
	num_links = 0 
	num_links_with_text = 0
	num_links_no_text = 0
	num_no_link = 0
	num_img_links = 0
	num_img_link_no_text = 0
	num_img_link_with_text = 0
	num_img_link_little_text = 0
	num_img_link_no_comment = 0

	num_video_link = 0

	num_external = 0
	num_internal = 0 

	posts = db.submission_list()
	#wayback_posts = db.wayback_submissions()

	for post in posts:
		text = post.get("submission_text") or ''
		num_post_words += len(text.split())
		comments = db.comment_list(post.get("_id"))
		num_comments += len(list(comments))
		for comment in comments: 
			num_comment_words += len(comment.get("comment_text").split())

		link = post.get("url")
		if link:
			print link,
			num_links += 1
			if is_image_link(link):
				print "\timg link"
				num_img_links += 1
				if len(text) == 0:
					num_img_link_no_text += 1
				else:
					if len(text) <= 20:
						num_img_link_little_text += 1
					num_img_link_with_text += 1
			if len(comments) == 0:
				num_img_link_no_comment 
			print ""
		else:
			num_no_link += 1

	## TO DO: For wayback stuff, use domain to figure out
	## if self.subreddit -- these are non-links. 

	# for post in wayback_posts:
	# 	text = post.get("submission_text")
	# 	num_post_words += len(text.split())
	# 	comments = db.comment_list(post.get("_id"))
	# 	num_comments += len(comments)
	# 	for comment in comments: 
	# 		num_comment_words += len(comment.get("comment_text").split())

	# 	link = post.get("url")
	# 	if link:
	# 		num_links += 1
	# 		if is_image_link(link):
	# 			num_img_links += 1
	# 			if len(text) == 0:
	# 				num_img_link_no_text += 1
	# 			else:
	# 				if len(text) <= 20:
	# 					num_img_link_little_text += 1
	# 				num_img_link_with_text += 1
	# 		if len(comments) == 0:
	# 			num_img_link_no_comment 
	# 	else:
	# 		num_no_link += 1


	num_posts = float(len(posts))
	avg_num_comments = num_comments / num_posts
	avg_num_comment_words = num_comment_words / num_posts
	avg_num_post_words = num_post_words / num_posts
	num_words = num_comment_words + num_post_words
	avg_num_total_words = num_words / num_posts 

	info = {
		'num posts': int(num_posts),
		'num comments': num_comments,
		'num words in post': num_post_words,
		'num words in comments': num_comment_words,
		'num words': num_words,
		'avg num of words total': avg_num_total_words,
		'avg num comments': avg_num_comments,
		'avg num words in posts': avg_num_post_words,
		'avg num words in comments': avg_num_comment_words,
		'num links': num_links,
		'num links with text': num_links_with_text,
		'num links with no text': num_links_no_text,
		'num no link': num_no_link,
		'num image links': num_img_links,
		'num image links with no text': num_img_link_no_text,
		'num image links with text': num_img_link_with_text,
		'num image links with little text': num_img_link_little_text,
		'num image links with no comments': num_img_link_no_comment
	}

	sr = stats[subreddit.get("subreddit_name")] 
	if sr in stats:
		for k, v in stats[sr].iteritems():
			stats[sr][k] += info[k]
	else:
		stats[sr] = info
	

# Sort by different factors 
mapping = []
def mysort(factor):
	mapping.append(factor)
	return sorted(stats.keys(), key=lambda k: stats[k][factor])

sorted_subreddits = (mysort('num posts'),
					 mysort('num comments'),
					 mysort('num words in post'),
					 mysort('num words in comments'),
					 mysort('num words'),
					 mysort('avg num of words total'),
					 mysort('avg num comments'),
					 mysort('avg num words in posts'),
					 mysort('avg num words in comments'),
					 mysort('num links'),
					 mysort('num links with text'),
					 mysort('num links with no text'),
					 mysort('num no link'),
					 mysort('num image links'),
					 mysort('num image links with no text'),
					 mysort('num image links with text'),
					 mysort('num image links with little text'),
					 mysort('num image links with no comments') )

## Save as csv so can use in excel chart 
for factor in mapping:
	print factor + ', ,',

print ''

for subreddit_index in range(len(subreddits)):
	for sorted_list in sorted_subreddits:
		print sorted_list[subreddit_index] + ', ,',
	print ''


