"""
Print stats from database. 
"""

# import sys
# import dokuwiki
# from dokuwiki import DokuWiki, DokuWikiError

# user = sys.argv[1]
# passwd = sys.argv[2]

# page = "http://intern.networkdynamics.org/doku.php?id=projects:improving_twitter_demographic_inference_through_topic_models"

# try:
#     wiki = DokuWiki(page, user, passwd)
#     print wiki
#     print wiki.pages.list
#     #print wiki.pages.get("reddit_dataset")
# except DokuWikiError as err:
# 	print err
# 	sys.exit(1)

# => 'Release 2012-10-13 "Adora Belle"'
#print wiki.version 

# print wiki.pages.list() # list all pages of the wiki
# print wiki.pages.list('my:namespace') # list all pages in the given namespace
# print wiki.pages.get('my:namespace:page') # print the content of the page


from redditDB import RedditDB
from utils import domain_frequencies, top_domains

rdb = RedditDB("mciot", "r3dd1tmorgane", "blacksun.cs.mcgill.ca", 31050, "reddit_topics")

### subreddit_collection ####
print "=========subreddit_collection========="
num_subreddits = rdb.num_subreddits()
print "Total number of subreddits:", num_subreddits
print ""

#### submission_collection ####
print "=========submission_collection========="
num_submissions = rdb.num_submissions()
print "Total number of submissions:", num_submissions
print "Average number of submissions/subreddit:", (float(num_submissions) / float(num_subreddits))
print ""
print "Number of cross-posted submissions:", rdb.num_xposts()
print "Number of subreddits involved in xposts: TODO" 
print ""
print "Number of submissions with links:", rdb.num_linked_submissions()
print "Number of submissions with links and no text:", rdb.num_only_linked_submissions()
print "Number of submissions with links where link content was crawled:", rdb.num_followed_submissions()
print ""
print "Stats by month: TODO"
print ""

#### comment_collection #### 
print "=========comment_collection========="
num_comments = rdb.num_comments()
print "Total number of comments:", num_comments
print "Average number of comments/submission:", (float(num_comments) / float(num_submissions))
print ""
print "Stats by month: TODO"

#### user_collection ####
print "=========user_collection========="
print "Total number of users:", rdb.num_users()
print ""

#### wayback ####
print "=========wayback_submissions========="
num_wayback_submissions = rdb.num_wayback_submissions()
num_wayback_comments = rdb.num_wayback_comments()
print "Total number of wayback submissions:", num_wayback_submissions
print "Total number of wayback comments:", num_wayback_comments
print "Average number of wayback comments/submission:", (float(num_wayback_comments) / float(num_wayback_submissions))
print "Total number of wayback subreddits: TODO"
if num_wayback_comments == 0:
	print "---No wayback comments: need to start collecting---"
print "Stats by year: TODO"
print ""


#TODO: Do this straight with mongodb aggregation 

## Popular domains ###
print "=========Popular domains:current collection========="
print "Finding frequencies of all domains..."
domain_freqs = domain_frequencies(rdb.submission_list())
print "Calculating top domains..."
top_20_domains = top_domains(domain_freqs, top=100)
print "DOMAIN\tCOUNT"
for domain, num in top_20_domains:
	print domain, "\t", num
print ""
print "=========Popular domains:wayback collection========="
print "Finding frequencies of all domains..."
domain_freqs_wb = domain_frequencies(rdb.get_wayback_submissions())
print "Calculating top domains..."
top_20_domains_wb = top_domains(domain_freqs_wb, top=100)
print "DOMAIN\tCOUNT"
for domain, num in top_20_domains_wb:
	print domain, "\t", num
print ""

### logging ####
print "=========logging information========="
types = rdb.log_types()
print 'TYPE', '\t', 'COUNT'
for typ in types:
	print typ, '\t', rdb.logged_errors_count(typ)