"""
This module provides a set of distance functions. Want
to minimize distance. So for similarity functions, make sure
to subtract from 1.  
"""

from itertools import izip
import math

def euclidean(v1, v2):
	pass

def cosine(a, b):
    ab_sum, a_sum, b_sum = 0, 0, 0
    for ai, bi in izip(a, b):
        ab_sum += ai * bi
        a_sum += ai * ai
        b_sum += bi * bi
    return 1 - ab_sum / math.sqrt(a_sum * b_sum)