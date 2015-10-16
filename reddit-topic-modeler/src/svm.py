"""
SVM using Scikit-learn's linear SVC algo. Uses liblinear. Takes a json file of twitter
user data, an output directory, and k, the number of folds. 

Example usage: python svm.py --features ../data/example.features.json --k 3 --dir ../data/twitter/svm_models/oct16
"""

import argparse
import json 
import numpy as np
from sklearn import svm
from sklearn import cross_validation 
from sklearn.externals import joblib

argparser = argparse.ArgumentParser(description="Train a linear SVM on twitter user features")
argparser.add_argument("--features", help="path to json file of training features", required=True)
argparser.add_argument("--k", help="number of folds for cross-validation", default=5)
argparser.add_argument("--dir", help="output directory where model will be stored", required=True)

params = argparser.parse_args()
filename = params.features
outputd = params.dir
k = int(params.k)

f = open(filename)
data = json.load(f)
f.close()

parameters = data["parameters"]
features = data["features"]
labels = data["parameters"]["labels"]
users = data["users"]

# Don't use length of features, which is also in json file,
# because doesn't contain topic meta-data as of now. 
num_datapoints = len(users)
item = users.popitem()
num_features = len(item[1]["feature_vector"])

print num_datapoints, "datapoints, each with", num_features, "features"

# Reinsert datapoint 
users[item[0]] = item[1]

# Create a numpy array of feature vectors and
# a numpy vector of responses (labels)
X = np.empty([num_datapoints, num_features])
Y = np.empty(num_datapoints)

row = 0
for userid, user_info in users.iteritems():
	for col, feature in enumerate(user_info["feature_vector"]):
		X[row,col] = feature
	Y[row] = labels[user_info["label"]]
	row += 1


# Train the linear SVM 
clf = svm.LinearSVC()
model = clf.fit(X, Y)

# Name of model 
name = ".".join(filename.split("/")[-1].split(".")[0:2])

print name

# This file will store model 
joblib.dump(model, outputd + "/" + name + "_model.pkl")

# This file will store model xval info 
infof = open(outputd + "/" + name + "_info.txt", "w")

# Perform k-fold cross validation to capture accuracy 
total = 0
originalk = k
kfolds = cross_validation.KFold(len(X), n_folds=k)
for train, test in kfolds:
	accuracy = clf.fit(X[train], Y[train]).score(X[test], Y[test])
	total += accuracy
	info = "Fold " + str(k) + ": " + str(accuracy) + "\n"
	print info,
	infof.write(info)
	k -= 1

# TODO: GRID SEARCH
# http://scikit-learn.org/stable/auto_examples/grid_search_digits.html

print "Average accuracy:", total / originalk

infof.close()


