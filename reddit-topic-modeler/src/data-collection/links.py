"""
Contains methods for scraping content
from links posted in Reddit submissions. 
"""

import urllib2
import httplib
import bs4
import HTMLParser

# :param url is the link to follow
# :param user_agent passed to request headers
def scrape_link(url, user_agent):
	try:
		request = urllib2.Request(url=url, headers={"User-agent": user_agent})
		html = urllib2.urlopen(request).read()
	# Generally this will have been caused by too many requests
	# error, which is becaused the link in question was a reddit
	# one. 
	except urllib2.URLError:
		#print "urllib2 error"
		return None 
	# Rarely arises with a faulty url. 
	except ValueError:
		#print "value error - faulty url?"
		return None
	except httplib.BadStatusLine:
		return None
	try:
		soup = bs4.BeautifulSoup(html)
	except HTMLParser.HTMLParseError:
		#print "HTML Parser error"
		return None
	return soup.body
