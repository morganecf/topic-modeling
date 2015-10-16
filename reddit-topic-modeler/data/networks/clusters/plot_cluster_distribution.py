import sys
import matplotlib.pyplot as plt

f = open(sys.argv[1]).read().splitlines()

data = []
for line in f:
	try:
		size, count = line.split('\t')
		data.append((float(size), float(count)))
	except ValueError:
		print 'bad line:', line
		continue

#data.sort(key=lambda d: d[1])
x = map(lambda d: d[0], data)
y = map(lambda d: d[1], data)

print 'Size range:', min(x), max(x)
print 'Count range:', min(y), max(y)

fig = plt.figure()
ax = plt.subplot(111)
ax.bar(x, y)	# width=100

#n, bins, patches = plt.hist(x, y, facecolor='green') # alpha?

plt.xlabel('Size')
plt.ylabel('Count')
plt.title('Xpost network cluster size distribution')
plt.axis([1, 100, 1, 200])
plt.grid(True)

plt.show()
