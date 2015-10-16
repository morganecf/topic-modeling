"""
"""

import os 
import gzip
import matplotlib 

matplotlib.use('Agg')

import matplotlib.pyplot as plt 

topicsf = open('../data/topics/top500.txt').read().splitlines()
#topicsf500 = open('../data/topics/top500.txt').read().splitlines()

lookat = ['technology', 'Music', 'politics', 'sports', 'atheism', 'StarWars']

mapping = {}

topics = {}

for i, topic in enumerate(topicsf):
	mapping[i] = {'topic': topic}
	topics[topic] = {
					   2010: {}, 
					   2011: {}, 
					   2012: {}, 
					   2013: {}, 
					   2014: {} 
					}

root = '../data/jgibbs/monthly/top500/'

for date in os.listdir(root):
	year = int(date.split('-')[0])
	month = date.split('-')[1]
	path = root + date + '/model.twords.gz'

	# if year != 2014:
	# 	continue 
	# print date 

	try:
		
		raw = gzip.open(path, 'rb').read().splitlines()

		for line in raw:
			print raw
		
		topic_indices = []
		for i, line in enumerate(raw):
			if line.startswith("Topic"):
				topic_indices.append(i)

		for x in range(0, len(topic_indices) - 1, 2):
			start = topic_indices[x]
			finish = topic_indices[x + 1]
			topic = mapping[int(raw[start].split()[1].replace(':', '').strip())]['topic']
			words = map(lambda w: w.split()[0].strip(), raw[start + 1:finish])
			topics[topic][year][month] = words 

			# if topic in lookat:
			# 	print '\t', topic, raw[start], start, finish
			# 	for word in words:
			# 		print '\t\t', word 


	except IOError:
		#print "No info for month:", month 
		continue 

ALL = {
	   2010: {}, 
	   2011: {}, 
	   2012: {}, 
	   2013: {}, 
	   2014: {}
	}

# If we repeat this process for all topics (e.g., comparing January vs. rest), we give a distribution
# of similarity values for each month.

### NOTE: Chose jaccard because other method relies on probability distrib of words 
### and the top 100 words all had very similar/same probabilities. 

def jaccard(A, B):
	A = set(A)
	B = set(B)
	top = len(list(A & B))
	bottom = len(list(A | B))
	return float(top) / bottom

month_vals = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

def similarities(topic, year, months):
	# If there is nothing in this year, don't compute anything
	if len(months) == 0:
		return

	# Compare everything to first month 
	try:
		first_month = '01'
		first_words = months[first_month] 
	except KeyError:
		# If first month (jan) unavailable, pick another one
		first_month = months.keys()[0]
		first_words = months[months.keys()[0]]

	jindexes = {}
	for month in month_vals:
		if month == first_month:
			continue 
		try:
			words = months[month]
		except KeyError:
			words = []

		# Find jaccard index between these two months 
		jindex = jaccard(first_words, words)
		jindexes[month] = jindex 
		try:
			ALL[year][month].append(jindex)
		except KeyError:
			ALL[year][month] = [jindex]

	ms = jindexes.keys()
	ms.sort()
	# vals = map(lambda m: jindexes[m], ms)
	# plt.plot(ms, vals)
	# plt.xlabel('Months')
	# plt.ylabel('Similarity')

	# plt.title(topic + ' - ' + str(year))
	# plt.savefig('../data/jgibbs/plots/per-month-sim/' + str(year) + '/' + topic)
	# plt.clf()

	# for m in ms:
	# 	print '\t\t', m, jindexes[m]


# Compute similarities 
# for topic, dates in topics.iteritems():
# 	print topic
# 	for year, months in dates.iteritems():
# 		#print '\t', year
# 		similarities(topic, year, months)
		# plt.savefig('../data/jgibbs/plots/per-year-sim/' + str(year) + '/' + topic)
	 # 	plt.clf()

def mean(distrib): return sum(distrib) / len(distrib)

# ALL now contains a distribution of similarity values for each month 
# Find the mean for each month for each year 

# Each month has a mean similarity associated with it (average similarity to january across topics)
# for year, months in ALL.iteritems():
# 	means = []
# 	for month in month_vals[1:]:
# 		try:
# 			distrib = months[month]
# 			means.append(mean(distrib))
# 		except KeyError:
# 			means.append(0)
# 	plt.plot(month_vals[1:], means)
# 	plt.xlabel('Months')
# 	plt.ylabel('Mean similarity to January across topics')
# 	plt.title(str(year))
# 	plt.savefig('../data/jgibbs/plots/mean_similarity_' + str(year))
# 	plt.clf()
		


