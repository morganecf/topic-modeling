import os

def notification(path):
	return "python ../../../src/notify.py morganeciot@gmail.com 'CC " + path + "' epiphyte"

# Ex: run('connected_components/user')
def run(component_dir_name):
	component_dirs = os.listdir(component_dir_name)

	# Iterate through all network type connected components 
	for CC in component_dirs:
		# Construct paths 
		path = os.path.join(component_dir_name, CC)
		normalized = os.path.join(path, 'normalized')
		regular = os.path.join(path, 'regular')
		normalized_int = os.path.join(path, 'normalized-int')
		regular_int = os.path.join(path, 'regular-int')

		# Run infomap on normalized and regular 
		infomap_norm = "python infomap.py " + normalized 
		infomap_reg = "python infomap.py " + regular 
		os.system(infomap_norm)

		os.system(infomap_reg)
		os.system(notification(normalized))
		os.system(notification(regular))

		# Run fast community detection on int weights 
		fcd_reg = "python communitydetection.py " + regular_int 
		fcd_norm = "python communitydetection.py " + normalized_int 
		os.system(fcd_reg)
		os.system(fcd_norm)
		os.system(notification(normalized_int))
		os.system(notification(regular_int))


run('../data/networks/user/connected_components/comment')
run('../data/networks/user/connected_components/submission')
run('../data/networks/user/connected_components/user')
