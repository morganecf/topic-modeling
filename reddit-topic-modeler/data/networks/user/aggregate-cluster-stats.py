# Aggregate cluster stats for all the different type of user networks 

import os

results = os.listdir("cluster-results")
output_path = 'cluster-results/results.csv'
output = open(output_path, 'w')
metadata = 'type,weighted,#hubs_removed,method,normalized,#clusters,#nodes,avg_cluster_size,median_cluster_size,#size_one-two,size_one-two%,largest,largest%,second_largest,second%,third_largest,third%,#>100,>100%,#<5,<5%'
output.write(metadata + '\n')

for result in results: 
	if result.endswith(".txt"):
		print result

		info = open('cluster-results/' + result).read().splitlines()[1:]
		distrib = info[:-5]
		stats = info[len(distrib) + 1:]

		distribution = {}
		for line in distrib:
			size, num = line.split('\t')
			distribution[int(size)] = int(num)

		num_clusters = float(stats[0][20:])
		num_nodes = float(stats[1][17:])

		num_size_onetwo = (distribution.get(1) or 0) + (distribution.get(2) or 0)
		size_onetwo_perc = "{0:.2f}".format((num_size_onetwo / num_clusters) * 100)

		sizes = distribution.keys()
		sizes.sort()
		largest = sizes[-1]
		largest_perc = "{0:.2f}".format((sizes[-1] / num_nodes) * 100)
		second = sizes[-2]
		second_perc = "{0:.2f}".format((sizes[-2] / num_nodes) * 100)
		third = sizes[-3]
		third_perc = "{0:.2f}".format((sizes[-3] / num_nodes) * 100)

		average_cluster_size = "{0:.2f}".format(sum(sizes) / float(len(sizes)))

		halfpoint = len(sizes) / 2
		if len(sizes) % 2 == 0:
			median_cluster_size = "{0:.2f}".format((sizes[halfpoint] + sizes[halfpoint - 1]) / 2.0)
		else:
			median_cluster_size = "{0:.2f}".format(sizes[halfpoint])

		greater100 = 0
		less5 = 0
		for k,v in distribution.iteritems():
			if k > 100:
				greater100 += v 
			elif k < 5:
				less5 += v 
		greater100_perc = "{0:.2f}".format((greater100 / num_clusters) * 100)
		less5_perc = "{0:.2f}".format((less5 / num_clusters) * 100)

		#type,weighted,#hubs_removed,method,normalized,
		network_type = result.split('_')[0]
		weighted = str(not ('unweighted' in result))
		normalized = str('norm' in result)
		method = 'map'
		if 'fcd' in result:
			method = 'fcd'
		num_hubs_removed = result.split('_')[2][1:]

		line = ','.join([network_type, weighted, num_hubs_removed, method, normalized, 
						str(int(num_clusters)), str(int(num_nodes)), str(average_cluster_size),
						str(median_cluster_size), str(num_size_onetwo), str(size_onetwo_perc),
						str(largest), str(largest_perc), str(second), str(second_perc), 
						str(third), str(third_perc), str(greater100), str(greater100_perc), 
						str(less5), str(less5_perc)])
		output.write(line + '\n')


