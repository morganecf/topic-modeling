"""
Convert network file to js file compatible for displaying network. 

"nodes": [
    {
      "id": "n0",
      "label": "A node",
      "x": 0,
      "y": 0,
      "size": 3
    }

"edges": [
    {
      "id": "e0",
      "source": "n0",
      "target": "n1"
    },
"""

import sys 
import json 

network = open(sys.argv[1]).read().splitlines()
out = open(sys.argv[2], 'w')

nodes = set()
edges = []

for i, edge in enumerate(network):
	try:
		s1, s2, weight = edge.split('\t')
		nodes.add(s1)
		nodes.add(s2)
		edges.append({
			'id': str(i),
			'source': s1,
			'target': s2
		})
	except ValueError:
		#print 'bad line:', edge 
		continue 

graph = {'nodes': [], 'edges': edges}
for node in nodes:
	graph['nodes'].append({'id': node, 'label': node, 'size': '3'})

datastr = 'var data = ' + str(graph) + ';'
out.write(datastr)
out.close()




