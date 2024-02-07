import numpy as np
import pandas as pd
import os
from qim_functions import extract_it, fscore_crit_bosons

def ph_sym_spect(s, nb, K):
    '''
    Obtain the critical energies (<3.0) of the p-h-symmetric spectrum for l-BFA model with U=0.5, g=5
    args:
        s [float]: bosonic bath exponent
        K [int]: number of states kept
        nb [int]: number of bosons per Wilson site
    returns:
        energies [DataFrame]: energies of the p-h-symmetric spectrum
    '''
    data_base = f'/blue/physics-dept/an.kandala/Localf_model/Boundary_databases/p_h_symmetry'
    ander_out = f'{data_base}/s={s}_K={K}_nb={nb}/last_runs/max.out'
    par = 'all'; phsym = True
    frame = fscore_crit_bosons(ander_out, 'all', [0,0])
    return frame
    

def LC_spect(s, nb):
    '''Obtains the level crossing spectrum for the single impurity model.
    args:
        s [float]: bosonic bath exponent
        nb [int]: number of bosons per Wilson site
    returns:
        LC_spec [DataFrame]: energies of the level crossing spectrum
    '''
    data_base = '/blue/physics-dept/an.kandala/Level_crossing/automated_s/Determining_ediff/runs_data_base'
    path = f'{data_base}/s={s}/nb={nb}/find_edc_runs'
    sub_dirs = [int(d.split('=')[1]) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    sub_dirs.sort()
    g = sub_dirs[-1]
    ander_out = f'{path}/g={g}/last_runs/max.out'
    frame = fscore_crit_bosons(ander_out, 'all', qno=[1,0])
    return frame