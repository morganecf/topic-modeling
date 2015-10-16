
# :param matrix is the numpy matrix
# :param documents is the list of documents
# Can use this to generate train or
# test sets. 
def toArff(matrix, documents, topics, filename):
	f = open("../data/"+filename, 'w')
	f.write("@RELATION reddit\n")
	for x in range(matrix.shape[1]):
		f.write("@ATTRIBUTE "+"p"+str(x)+"\tNUMERIC\n")
	f.write("@ATTRIBUTE class\t{0,1,2,3,4,5,6}\n\n")
	f.write("@DATA\n")
	for i,row in enumerate(matrix):
		topic = topics.index(documents[i].topic)
		for cell in row:
			f.write(str(cell)+',')
		f.write(str(topic)+"\n")
	f.close()

# :param data is the numpy matrix
def toCSV(data, topics, documents, Xfilename, Yfilename):
	Xf = open("../data/files/"+Xfilename, 'w')
	Yf = open("../data/files/"+Yfilename, 'w')
	for i, row in enumerate(data):
		topic = topics.index(documents[i].topic)
		for cell in row:
			Xf.write(str(cell)+',')
		Xf.write('\n')
		Yf.write(str(topic)+'\n')
	Xf.close()
	Yf.close()
