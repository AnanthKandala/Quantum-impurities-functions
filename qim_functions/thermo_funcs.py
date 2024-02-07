import pandas as pd
import re
import numpy as np
from .misc_funcs import pdiff
from scipy.signal import find_peaks

def zavg(T, y):
    '''
    calculates the average of the y at the lowest temperature of iteration N and the highest temperature of iteration N+1.
    '''
    T_clean = np.empty(len(np.unique(T)))
    y_clean = np.empty(len(np.unique(T)))
    i = 0
    c = 0
    while i < len(T):
        if i < len(T)-2 and T[i] == T[i+1]:
            T_clean[c] = T[i]
            y_clean[c] = 0.5*(y[i] + y[i+1])
            i += 2
        else:
            T_clean[c] = T[i]
            y_clean[c] = y[i]
            i += 1
        c += 1
    return T_clean, y_clean


def extract_matrix_elems(ander_out, operator):
    '''
    Extracts the matrix elements as a function of temperature from the output file
    args:
        ander_out [str]: ander.out file
        operator [str]: name of the operator'''
    with open(ander_out, 'r') as f:
        all_lines = f.readlines()
    T = []
    matrix_elems = []
    for line in all_lines:
        if f'<{operator}>' in line:
            patternt = r'\s*T\s*=\s*([\d\.-]+E[+-]\d+)'
            matcht = re.search(patternt, line)
            if matcht:
                T.append(float(matcht.group(1)))
            else:
                print('No match for T')

            patternd = fr'\s*<{operator}>\s*=\s*([\d\.-]+(E[+-]\d+)?)'
            matchd = re.search(patternd, line)
            if matchd:
                matrix_elems.append(float(matchd.group(1)))
            else:
                print(line)
                print(f'No match for {str}')
    return T, matrix_elems


# def flow_T(level):
#     '''returns the temperatures where the level reaches the critical plateu and the flow away to a stable fixed point.'''
#     # check if all the iterations are even or odd
#     if np.all(level['n'].to_numpy(int)%2 == 0) or np.all(level['n'].to_numpy(int)%2 == 1):
#         run_type = 'fermionic'
#     else:
#         run_type = 'bosonic'
#     list_n = list(flow_points(level).values())
#     return it_temp(list_n, run_type)
    
def it_temp(N, run_type):
    '''returns the lowest temperature at iteration N.
        args: N(int):-->iteration number, Lambda(float):-->NRG Lambda value (=9)
        run_type(str):-->type of run: 'bosonic' or 'fermionic'
        returns: T(float):-->temperature'''
    # if isinstance(N, int) or isinstance(N, float):
    Lambda = 9.0
    factor = {'bosonic': 1, 'fermionic': 2}
    assert run_type in factor.keys(), "run_type must be 'bosonic' or 'fermionic'"
    alpha = 0.5*Lambda*(1 + Lambda**-1)
    beta_bar_max = 0.6
    fac = factor[run_type]
    T = (alpha*Lambda**(-N/fac))/beta_bar_max
    return T
    # if isinstance(N, np.ndarray) or isinstance(N, list):
        # T_list = [it_temp(int(n), run_type) for n in N if not np.isnan(n)]
        # return T_list
    # else:
        # raise TypeError(f'N must be either an numer or a numpy array/list. It is of type {type(N)}')

def n_star(level):
    ''' using find_peaks method in scipy.signal to find the peaks of the signal'''
    peaks, _ = find_peaks(level['energy'].diff().diff())
    if len(peaks)>0:
        n_star = level['n'].iloc[min(peaks)]
    else:
        n_star = np.nan
    return n_star

def n_crit(level):
    '''find the local minima of the level for n<n_star'''
    n_max = n_star(level)
    selected_level = level.query(f'n < {n_max}')
    if np.isnan(n_max):
        minimas, _ = find_peaks(-selected_level['energy'].diff().abs())
        return level['n'].iloc[min(minimas)]
    else:
        selected_level = level.query(f'n < {n_max}')
        minimas, _ = find_peaks(-selected_level['energy'].diff().abs())
        if len(minimas)>0:
            n_crit = selected_level['n'].iloc[min(minimas)]
        else:
            n_crit = np.nan
    return n_crit

def flow_T(level):
    '''finds the iterations where the level can be interpreted as a critical plateu or a flow away from the critical plateu (n_cri, n_flat)
       args: level(data_frame):-->data frame containing n vs energy
       returns: [n_crit, n_star]:'''
    
    E = level['energy'].to_numpy()
    if np.all(level['n']%2 == 0) or np.all(level['n']%2 == 1):
        runtype = 'fermionic'
    else:
        runtype = 'bosonic'

    #Identify n_star
    y = np.abs(pdiff(E[1:], E[:-1]))
    peaks, _ = find_peaks(y, [0.6])
    if len(peaks)==0:
        peaks, _ = find_peaks(y)
        print(peaks)
        if len(peaks)!=0:
            n_star = level['n'].iloc[min(peaks)+1]
        else:
            n_star = np.inf
    else: #no peaks found
        n_star = level['n'].iloc[min(peaks)+1]

    #Identify n_crit
    minimas, _ = find_peaks(-y, width=2)
    if len(minimas):
        n_crit = level['n'].iloc[min(minimas)+1]
        assert n_crit < n_star, 'n_crit should be smaller than n_star'
    else: #no flat iteration found
        n_crit = np.inf
    return {'n_crit':n_crit, 'n_star':n_star}, {'T_crit': it_temp(n_crit, runtype), 'T_star': it_temp(n_star, runtype)}



# def inflection_point(level, opt_type:str):
#     E = level['energy'].to_numpy()
#     N = level['n'].to_numpy()
#     N_diff = N[:-1]
#     E_diff = np.abs(np.diff(E))
#     '''Obtains the first local max/min of the function f:x->y, depending on opt_type.'''
#     opt_choices = {'max': np.greater, 'min': np.less}
#     inflection_indices = argrelextrema(np.column_stack((N_diff, E_diff)), opt_choices[opt_type], axis=0, order=1)
#     return [N_diff[i] for i in inflection_indices[0]]


