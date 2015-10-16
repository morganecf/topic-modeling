"""
This module provides weighting functions for document vectors. 
"""

import math

def term_frequency(frequency, **kwargs):
	return frequency

def boolean(frequency, **kwargs):
	if frequency > 0:
		return 1
	else:
		return 0

def tfidf(frequency, **kwargs):
	return frequency * (math.log(float(kwargs['N']/float(kwargs['ni']))))

def tfidf_doc_length(frequency, **kwargs):
	numerator = tfidf(frequency, **kwargs)
	col = kwargs['col']
	data = kwargs['data']
	denominator = math.sqrt(sum( map(lambda cell: math.pow(cell,2), data[col, :]) ))
	return numerator/denominator


