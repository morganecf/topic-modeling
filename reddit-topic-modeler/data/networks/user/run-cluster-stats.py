#
# Run cluster_stats.py over all user cluster combinations 
# (combinations of hubs removed, fcd vs. map, user vs. commnet vs. submission, etc.)
# Usage: python cluster_stats.py <clustering result dir> <output file path> 
# Example: python cluster_stats.py ../data/networks/user/connected_components/submission/submission_unweighted_h10/regular-int/fcd_results/ ../data/networks/user/submission_unweighted_h10_fcd.clusters
#

import os 

# user/user_weighted_h500/regular-int/fcd_results
def output_file(input_dir):
	name = input_dir.split('/')[1]
	if 'normalized' in input_dir:
		name += '_norm'
	if 'fcd' in input_dir:
		name += '_fcd'
	elif 'infomap' in input_dir:
		name += '_map'
	name += '.clusters'
	path = '../data/networks/user/' + name 
	return path


directories = ['comment', 'submission', 'user']
hub_removals = [10, 50, 100, 500, 1000]

for directory in directories: 
	for hr in hub_removals:
		weighted = directory + '/' + directory + '_weighted_h' + str(hr)
		unweighted = directory + '/' + directory + '_unweighted_h' + str(hr)

		weighted_map = weighted + '/regular/infomap_results'
		weighted_fcd = weighted + '/regular-int/fcd_results'
		weighted_norm_map = weighted + '/normalized/infomap_results'
		weighted_norm_fcd = weighted + '/normalized-int/fcd_results'

		unweighted_map = unweighted + '/regular/infomap_results'
		unweighted_fcd = unweighted + '/regular-int/fcd_results'
		unweighted_norm_map = unweighted + '/normalized/infomap_results'
		unweighted_norm_fcd = unweighted + '/normalized-int/fcd_results'

		inputs = (weighted_map, weighted_fcd, weighted_norm_map, weighted_norm_fcd,
				  unweighted_map, unweighted_fcd, unweighted_norm_map, unweighted_norm_fcd)

		# in: ../data/networks/user/connected_components/submission/submission_unweighted_h10/regular-int/fcd_results/
		# out: ../data/networks/user/submission_unweighted_h10_fcd.clusters
		for input_dir in inputs:
			out = output_file(input_dir)
			input_dir = '../data/networks/user/connected_components/' + input_dir 
			command = 'python cluster_stats.py ' + input_dir + ' ' + out 

			print command 
			os.system(command) 




