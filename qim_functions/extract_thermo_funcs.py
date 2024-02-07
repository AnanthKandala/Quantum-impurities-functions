import pandas as pd
import numpy as np
from .thermo_funcs import zavg, extract_matrix_elems
import re

###############STATIC THEROMODYNAMIC QUANTITIES##################
def charge(ander_out):
    '''Extracts <n_d> as a function of temperature from the ander.out file.
       args: location of the ander.out file
        returns: pandas dataframe with columns 'T' and 'nd'
    '''
    T, nd = extract_matrix_elems(ander_out, 'n_d')
    T, nd = zavg(T, nd) #averaging over the values of nd at the same temperature
    data = pd.DataFrame({'T':T, 'nd': nd})
    return data

def spin(ander_out):
    '''Extracts Chi_s vs T as a function of temperature from the ander.out file.
       args: location of the ander.out file, h ---> magnetic field
        returns: pandas dataframe with columns 'T' and 'chi'
    '''
    with open(ander_out, 'r') as f:
        all_lines = f.readlines()
    T = []
    tchi = []
    for line in all_lines:
        if 'T*loc' in line:
            parts = line.strip().split()
            T.append(float(parts[3]))
            tchi.append(float(parts[-1]))
    T, tchi = zavg(T, tchi) #averaging over the values of nd at the same temperature
    data = pd.DataFrame({'T':T, 'chi': tchi/T})
    return data


def simpz(ander_out):
    '''Extracts simpz vs T as a function of temperature from the ander.out file.
       args: location of the ander.out file
        returns: pandas dataframe with columns 'T' and 'simpz'
    '''
    with open(ander_out, 'r') as f:
        all_lines = f.readlines()
    T = []
    simpz = []
    for line in all_lines:
        if 'T*loc' in line:
            parts = line.strip().split()
            T.append(float(parts[3]))
            simpz.append(float(parts[6]))

    T, simpz = zavg(T, simpz) #averaging over the values of nd at the same temperature
    data = pd.DataFrame({'T':T, 'simpz': simpz})
    return data



def N_a(ander_out):
    '''Extracts <N_a> as a function of temperature from the ander.out file.
       args: location of the ander.out file
        returns: pandas dataframe with columns 'T' and '<N_a>'
    '''
    with open(ander_out, 'r') as f:
        all_lines = f.readlines()
    T = []
    Na = []
    for line in all_lines:
        if '<N_a>' in line:
            patternt = r'\s*T\s*=\s*([\d\.-]+E[+-]\d+)'
            matcht = re.search(patternt, line)
            if matcht:
                T.append(float(matcht.group(1)))
            else:
                print('No match for T')

            patternd = r'\s*<N_a>\s*=\s*([\d\.-]+(E[+-]\d+)?)'
            matchd = re.search(patternd, line)
            if matchd:
                Na.append(float(matchd.group(1)))
            else:
                print(line)
                print('No match for N_a')

    if len(T) == 0:
        for line in all_lines:
            if '<n_a>' in line:
                patternt = r'\s*T\s*=\s*([\d\.-]+E[+-]\d+)'
                matcht = re.search(patternt, line)
                if matcht:
                    T.append(float(matcht.group(1)))
                else:
                    print('No match for T')

                patternd = r'\s*<n_a>\s*=\s*([\d\.-]+(E[+-]\d+)?)'
                matchd = re.search(patternd, line)
                if matchd:
                    Na.append(float(matchd.group(1)))
                else:
                    print(line)
                    print('No match for n_a')
        
    T, Na = zavg(T, Na) #averaging over the values of nd at the same temperature
    data = pd.DataFrame({'T':T, 'N_a': Na})
    return data


def hybrid(ander_out):
    ''' extracts the matrix elements of O_1 = sum_s (d+_e,s f_0,e,s + H.c.) as a function of the temperature
        args: location of the ander.out file
        returns: pandas dataframe with columns 'T' and 'hyb'
    '''
    T, hyb = extract_matrix_elems(ander_out, 'hyb')
    T, hyb = zavg(T, hyb) #averaging over the values of nd at the same temperature
    data = pd.DataFrame({'T':T, 'hyb': hyb})
    return data