"""
Script to get all user ids and tweets, clean them,
and output to csv file to use with llda model. 
"""

import sys
import MySQLdb as mysql
from utils import clean

host = "blacksun.cs.mcgill.ca"
user = "mciot"
db = "roost"

labels = { "ideology": [1,2], 
           "gamers": [3,4],
           "gender": [5,6],
           "party": [7,8] }

try:
    passwd = sys.argv[1]
    name = sys.argv[2]
    pair = labels[name]
except:
    print "Please provide a correct label name: ideology, gamers, gender, party."
    sys.exit(0)


def get_users_for_label(label):
    cursor.execute("SELECT user_id FROM user_label_assignments "
                        "WHERE label_id = %s", label)
    user_ids = [row[0] for row in cursor.fetchall()]
    return user_ids

def get_tweets_for_user(user_id):
    cursor.execute("SELECT status_text, tweet_timestamp FROM user_tweets "
                        "WHERE user_id = %s", user_id)
    result = cursor.fetchall()
    return result


db = mysql.connect(host=host, user=user, passwd=passwd, db=db)
cursor = db.cursor()

tweetfile = "../data/twitter/llda_tweets."+name+".csv"
userfile = "../data/twitter/llda_userids."+name+".txt"

llda_input = open(tweetfile, "wt")  # For documents (tweets)
user_ids = open(userfile, "wt")   # For user ids (line number corresponds to tweet)

for label in pair:
    userids = get_users_for_label(label)
    # Each user gets one doc 
    for user in userids:
        tweets = get_tweets_for_user(user)
        # Amalgamate all of user's tweets in one line 
        llda_line = ' '.join(map(lambda tweet: clean(tweet[0], uni=False), tweets))
        llda_input.write("None,"+llda_line+"\n")
        user_ids.write(str(user)+"\n")

print "Saving tweets in", tweetfile
print "Saving user ids in ", userfile

llda_input.close()
user_ids.close()


        

