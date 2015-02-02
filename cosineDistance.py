__author__ = 'Mike Housky'
# Adapted from http://stackoverflow.com/questions/18424228/cosine-similarity-between-2-number-lists

import math

def cosine_similarity(v1,v2):
    "compute cosine similarity of v1 to v2: (v1 dot v1)/{||v1||*||v2||)"
    sumxx, sumxy, sumyy = 0, 0, 0
    for i in range(len(v1)):
        x = v1[i]; y = v2[i]
        sumxx += x*x
        sumyy += y*y
        sumxy += x*y
    return sumxy/math.sqrt(sumxx*sumyy)

def cosine_distance(v1, v2):
    return 1 - cosine_similarity(v1,v2)