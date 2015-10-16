"""
This module provides functions for reducing the dimensionality of 
a document by term matrix. 
"""

from numpy import linalg
from numpy import dot, diag

def LSA(matrix, dimensionality, method):
	# Decompose
	u, sigma, vt = linalg.svd(matrix)
	
	# Reduce dimensionality of matrices 
	u = u[:, :dimensionality]
	sigma = diag(sigma)[:dimensionality, :dimensionality]
	vt = vt[:dimensionality, :]

	# Get the new doc word matrix of reduced rank
	# Now to query 
	lowrank_matrix = dot(u, dot(sigma, vt))
	return lowrank_matrix

def PCA(matrix, dimensionality, method):
	pass
