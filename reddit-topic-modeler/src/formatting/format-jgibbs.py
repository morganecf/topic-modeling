"""
Formats data into JGibbs LLDA- and LDA-compatible input, which has format:
[label] term_1 term_2 term_3 ... term_n

Takes as input data that was formatted for hdp-c, lda-c, etc., in data/formatted_data. 
"""

import argparse

argparser = argparse.ArgumentParser(description="Format data into JGibbs LLDA-compatible input")
argparser.add_argument("--data", help="path to data directory", required=True)
argparser.add_argument("--output", help="path to output directory", required=True)
args = argparser.parse_args()

path = args.data
output = args.output 

if not path.endswith("/"):
	path += "/"
if not output.endswith("/"):
	output += "/"

wordlist = open(path + "words.txt").read().splitlines()
words = {}
for i,w in enumerate(wordlist):
	words[i] = w

labellist = open(path + "labels_new.txt").read().splitlines()
datalist = open(path + "matrix.txt").read().splitlines() 

output_llda = open(output + "jgibbs-llda.txt", "w")
output_lda = open(output + "jgibbs-lda.txt", "w")

# matrix.txt format: 248  7777:1 3175:1 1454:1 49:1 34389:1 48550:1 5837:6 2329:1 1595:1 (wordindex:freq)
for i, line in enumerate(datalist):
	newline = ''
	info = line.split()[1:]
	for pair in info:
		word_index = int(pair.split(':')[0])
		word = words[word_index]
		newline += word + ' '
	output_llda.write('[' + labellist[i] + '] ' + newline + '\n')
	output_lda.write(newline + '\n')

output_llda.close()
output_lda.close()

