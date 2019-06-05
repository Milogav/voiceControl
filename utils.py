import numpy as np

def printInPlace(text):
    print('\r'+text+'\t'*5,end='',sep = '')

def getMaxIntensity(audioArray):
    return np.max(np.abs(audioArray))
