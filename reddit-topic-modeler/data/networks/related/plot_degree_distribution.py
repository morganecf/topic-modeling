import matplotlib.pyplot as plt

f = open('degree_distribution.txt').read().splitlines()

data = []
for line in f:
	degree, count = line.split('\t')
	try:
		data.append((float(degree), float(count)))
	except ValueError:
		print 'bad line:', line
		continue

#data.sort(key=lambda d: d[1])
x = map(lambda d: d[0], data)
y = map(lambda d: d[1], data)

print 'Degree range:', min(x), max(x)
print 'Count range:', min(y), max(y)

fig = plt.figure()
ax = plt.subplot(111)
ax.bar(x, y)	# width=100

#n, bins, patches = plt.hist(x, y, facecolor='green') # alpha?

plt.xlabel('Degree')
plt.ylabel('Count')
plt.title('Related subreddits network degree distribution')
plt.axis([1, 400, 1, 1000])
plt.grid(True)

plt.show()
