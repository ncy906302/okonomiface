import numpy as np

def CalculateSimilarity(a,b):
    a = np.array(a[:])
    b = np.array(b[:])
    return sum(a*b)/ (sum(a*a) **0.5 ) * (sum(b*b) **0.5)