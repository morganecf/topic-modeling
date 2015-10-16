"""
Creates tweet and corresponding id file from labeled 
user profiles and their tweets (from crowdflower data).
Only does male and female. Takes a limit (number of tweets per user). 

Usage: python crowdflower_to_text.py <limit> <output dir>
"""

import sys
from utils import clean 

profile_file = "../../labeled_user_profiles.txt"
tweetsd = "../../../tweets-by-user"

limit = int(sys.argv[1])
outputd = sys.argv[2]

def get_tweets_for_user(user_id):
    path = tweetsd + "/tweets-user-" + str(user_id) + ".txt"
    tweets = []
    with open(path, 'r') as f:
        for index, line in enumerate(f):
            if index >= limit:
                return clean(" ".join(tweets), False)
            info = line.split("\t")
            if len(info) != 5:
                print info[-2]
            tweets.append(info[-1].strip())

if not outputd.endswith("/"):
    outputd += "/"

# tweets = open(outputd + "tweets_" + str(limit) + ".csv", "w")
# ids = open(outputd + "ids_" + str(limit) + ".csv", "w")

with open(profile_file, 'r') as f:
    for index, line in enumerate(f):
        info = line.split("\t")
        label = info[-1]
        user_id = info[0].strip()
        label = int(label.strip())
        # Only keep males and females 
        if label == 1 or label == 2:
            text = get_tweets_for_user(user_id)
            # if text:
            #     ids.write(user_id+"\n")
            #     tweets.write(text+"\n")
