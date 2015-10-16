
class Comment:
	def __init__(self, name):
		self.name = name
		self.children = []

	def add(self, child):
		self.children.append(child)

	def getChildren(self):
		return self.children

def unique(alist):    # Fastest order preserving
	if not alist:
		return alist
	set = {}
	return [set.setdefault(e,e) for e in alist if e not in set] 

def getAllChildren_helper(comment, total): 
	children = comment.getChildren()
	if not children:
		return []
	for child in children:
		total.append(child)
		getAllChildren_helper(child, total)
	return total 

def getAllChildren(comment):
	children = getAllChildren_helper(comment, [])
	return unique(children)

def printComments(comments):
	if not comments:
		print "",
	else:
		comms = [comm.name for comm in comments]
		print comms,

def layer(comments, layers, layernum, offset):
	print "start:",
	printComments(comments)
	print layers, layernum
	for x in range(0, len(comments)):
		index = x + offset
		print "in loop:", x, comments[x].name, index
		if not layers[index]:
			layers[index] = layernum
			sub = getAllChildren(comments[x])
			print "sub:",
			printComments(sub)
			if sub:
				print "chidlren exist. recursive call"
				layer(sub, layers, layernum + 1, x + offset + 1)
				next = len(sub) + x + 1
				x = next 
				print "next:", next
			else:
				print "no children"


a = Comment("a")
b = Comment("b")
c = Comment("c")
d = Comment("d")
e = Comment("e")
f = Comment("f")
g = Comment("g")
h = Comment("h")
i = Comment("i")

# a.add(b)
# a.add(h)
# a.add(i)
# b.add(c)
# b.add(g)
# c.add(d)
# c.add(f)
# d.add(e)

a.add(b)
a.add(c)
a.add(d)
a.add(e)
a.add(f)
a.add(g)
b.add(c)
b.add(d)
b.add(e)
c.add(d)
f.add(g)

comments = [a, b, c, d, e, f, g, h, i]
layers = [0]*len(comments)


layer(comments, layers, 1, 0)

print layers
