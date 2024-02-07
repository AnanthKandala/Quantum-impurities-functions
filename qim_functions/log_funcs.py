import numpy as np
import pandas as pd

#Functions to process ander.log file
def log_couplings(infile):
    '''
    extract the values closest to the critical point from ander.log file.
    returns the lower and upper bounds on the critical coupling: [gmin, gmax]
    '''
    f = open(infile, "r")
    A = f.readlines()
    i = 1 
    while i<len(A):
        line = A[::-1][i]
        if '>' in line:
            gg = A[::-1][i-1].split()
            gmin = float(gg[0])
            gmax = float(gg[1])   
            return [gmin, gmax]
        i += 1 

    # if '***' in A[-1] and 'not' not in A[-1]: #runs have converged
    #     gg = A[-2].split()
    #     gmin = float(gg[0])
    #     gmax = float(gg[1])
    #     return [gmin, gmax]
    # else:
    #     return [0, 0]


def extract_t_star(infile):
    '''
    extracts the variation of T* w.r.t fractional distance for the critical point
    returns two dictionaries: T = {1:[], 2:[]}, G = {1:[], 2:[]} 
    T contains the T* for each phase. G contains abs(-1 + g/gc) for each phase'''
    T = {1:[], 2:[]}
    G = {1:[], 2:[]}
    gg = log_couplings(infile)
    gc = np.mean(gg, dtype='float64')
    with open(infile, 'r') as f:
        all_lines = f.readlines()
    for line in all_lines:
        if '>' in line:
            phase = int(line.split()[-1])
            if phase in [1,2]:
                T[phase].append(float(line.split()[2]))
                G[phase].append(abs(-1 + float(line.split()[1])/gc))
    return T, G

def log_simpz(infile):
    '''Reads the saturation value of simpz from the log file as a function of the field
    example: simpz \propt g^\beta or simpz \propt g1/\delta
    '''
    with open(infile, 'r') as f:
        lines = f.readlines()
    split_lines = []
    for line in lines:
        a = line.split()
        split_lines.append([float(a[1]), float(a[2]), int(a[3]), int(a[4]), float(a[5])])
    df = pd.DataFrame(split_lines, columns=['field', 'simpz', 'N', 'phase', 'tol'])
    return df