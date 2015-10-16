import sys

f = sys.argv[1]
lines = open(f).read().splitlines()
for line in lines:
	print ','.join(line.split('\t'))


