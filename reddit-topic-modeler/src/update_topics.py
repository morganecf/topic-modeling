"""
Call the update topics method to get new reddit topics in database. 
"""

from scraper import Scraper

s = Scraper("Reddit topics v01", "blacksun.cs.mcgill.ca", 31050, "", "r3dd1tmorgane", "reddit_topics")
s.update_topics(5000)
