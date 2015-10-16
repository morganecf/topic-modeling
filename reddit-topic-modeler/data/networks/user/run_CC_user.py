import os

networks = os.listdir("hubs-removed")
for network in networks:
	if network.endswith(".tsv"):
		dir_name = network.replace(".tsv", "")
		if dir_name.startswith("comment"):
			path = "connected_components/comment/" + dir_name 
		elif dir_name.startswith("submission"):
			path = "connected_components/submission/" + dir_name 
		elif dir_name.startswith("user"):
			path = "connected_components/user/" + dir_name 

		command = "python ../../../src/connected_components.py hubs-removed/" + network + " " + path + " directed -1" 
		os.system(command)
		send = "python ../../../src/notify.py morganeciot@gmail.com " + command + " "


# python connected_components.py ../data/networks/user/hubs-removed/comment_unweighted_h10.tsv 
# 	../data/networks/user/connected_components/comment/comment_unweighted_h10 directed  -1 

