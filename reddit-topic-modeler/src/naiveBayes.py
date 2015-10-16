"""
Naive Bayes classifier using scikit-learn's multinomial naive bayes. Naive Bayes makes the 
naive assumption that features are independent, so P(y|x1...xn) = P(y)*P(x1....xn|y)/P(x1...xn)
= [P(y)*P(x1|y)*P(x2|y)*....*P(xn|y)]/P(x1)...P(xn).

Train usage: python naiveBayes.py --data <training data> --labels <corresponding labels> --words <unique words list> --dir <results dir>
Test usage: python naiveBayes.py --data <test data> --labels <corresponding labels> --dir <results dir>
"""

import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from itertools import izip
from sklearn.naive_bayes import MultinomialNB
from sklearn.externals import joblib
from sklearn.metrics import confusion_matrix

def vectorize(line, num_words):
	v = np.zeros(num_words)
	data = line.split()[1:]
	for x in data:
		x = x.split(":")
		index = int(x[0])
		count = int(x[1])
		v[index] = count
	return v

def process():
	# Open word file  
	words = open(wordsf).read().splitlines()
	num_words = len(words)
	# Just need length 
	del words

	# Process data into X (data) and y (labels)
	Xraw = []
	yraw = []

	with open(dataf) as data, open(labelf) as labels:
		for line, label in izip(data, labels):
			Xraw.append(vectorize(line, num_words))
			yraw.append(int(label))

	# Transform predictors and labels into numpy matrix
	X = np.vstack(Xraw)
	y = np.asarray(yraw)
	return X, y

# Train a model 
def train():
	X, y = process()
	model = MultinomialNB()
	model.fit(X, y)
	joblib.dump(model, outputd + "/model.pkl")

# Test a given model 
def test():
	X, y = process()
	model = joblib.load(modelf)
	yhat = model.predict(X)

	results = open(outputd + "/predicted.txt", "w")
	info = open(outputd + "/results.txt", "w")

	# Save predictions 
	for entry in np.nditer(yhat):
		results.write(str(entry)+"\n")
	results.close()

	# Save accuracy 
	num_wrong = (y != yhat).sum()
	perc_correct = (float(y.size - num_wrong) / float(y.size)) * 100
	info.write("Num unique labels: " + str(np.unique(y).size) + "\n")
	info.write("Num mislabeled: " + str(num_wrong) + "\n")
	info.write("Num labeled correctly: " + str(y.size - num_wrong) + "\n")
	info.write("Total: " + str(y.size) + "\n")
	info.write("Accuracy: " + str(perc_correct) + "%\n")
	info.close()

	# Save confusion matrix
	conf = confusion_matrix(y, yhat)
	np.savetxt(outputd + "/confusion_matrix.txt", conf, delimiter=",")

	# Save confusion matrix plot 
	# plt.plot(conf)
	# plt.title("Confusion matrix")
	# plt.colorbar()
	# plt.ylabel("Actual")
	# plt.xlabel("Predicted")
	# plt.savefig(outputd + "/confusionmatrix")

def infer():
	# Open word file  
	words = open(wordsf).read().splitlines()
	num_words = len(words)
	# Just need length 
	del words

	# Process data into X matrix
	Xraw = []
	with open(dataf) as data:
		for line in data:
			Xraw.append(vectorize(line, num_words))
	X = np.vstack(Xraw)

	# Load model and predict topics 
	model = joblib.load(modelf)
	yhat = model.predict(X)

	# Save predictions 
	fname = dataf.split("/")[-1].replace(".txt", "").replace(".csv", "") + "_predicted.txt" 
	results = open(outputd + "/" + fname, "w")
	for entry in np.nditer(yhat):
		results.write(str(entry)+"\n")
	results.close()


# Get inputs 
argparser = argparse.ArgumentParser(description="Train or test a Naive Bayes model.")
argparser.add_argument("--data", help="train or test data", required=True)
argparser.add_argument("--labels", help="train or test labels")
argparser.add_argument("--words", help="list of unique words", required=True)
argparser.add_argument("--dir", help="output directory", required=True)
argparser.add_argument("--model", help="path to saved (pickled) model file")

params = argparser.parse_args()

dataf = params.data
labelf = params.labels
wordsf = params.words
outputd = params.dir
modelf = params.model 

if outputd.endswith("/"):
	outputd = outputd[:-1]

# Train or test 
if modelf:
	if labelf:
		test()
	else:
		infer()
else:
	train()


