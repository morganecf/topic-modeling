import os
import fileinput 

logfiles = os.listdir("./integer-log")
normfiles = os.listdir("./integer-norm")

for lf in logfiles:
	for line in fileinput.input("./integer-log/" + lf, inplace=True):
		info = line.split("\t")
		try:
			newline = [info[0], info[1], str(int(float(info[2])))]
			print "\t".join(newline)
		except IndexError:
			print line

for lf in normfiles:
	for line in fileinput.input("./integer-norm/" + lf, inplace=True):
		info = line.split("\t")
		try:
			newline = [info[0], info[1], str(int(float(info[2])))]
			print "\t".join(newline)
		except IndexError:
			print line