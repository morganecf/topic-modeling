import preprocessors as pre

def clean_up(text):
	text = pre.clean(text)
	text = pre.filter_by_list(text, pre.stopwords_long)
	text = pre.remove_non_ascii(text)
	return text

lines = open("../../../all-age-dataset.txt").read().splitlines()

newlines = open("../../../labeled_user_age_profiles.txt", "w")

idsf = open("../data/twitter/crowdflower/ids_age.csv", "w")
tweetsf = open("../data/twitter/crowdflower/tweets_age.csv", "w")

for line in lines:
	uid, age, username, json, date = line.split('\t')
	newlines.write(uid + '\t' + username + '\t' + json + '\t' + date + '\t' + age + '\n')

	# Get user's corresponding tweets
	tweets = ''
	try:
		with open("../../../tweets-by-user-age/tweets-user-" + uid + ".txt", 'r') as f:
			for line in f:
				tweets += clean_up(line.split('\t')[-1])
	except IOError:
		# If not in dataset ignore this user 
		print uid, 'not in ds'
		continue 

	idsf.write(uid + '\n')	
	tweetsf.write(tweets.strip() + '\n')

