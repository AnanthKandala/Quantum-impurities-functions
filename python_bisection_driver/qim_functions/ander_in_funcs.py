import numpy as np
from qim_functions import ander_in
from .log_funcs import log_couplings

def eff_ander_in(path, tuning_var_name):
    '''reads the effective inputs of a run
    args: path (str): path to the run directory, tuning_var_name (str): name of the tuning variable
    returns: inputs (dict): effective inputs of the run'''
    inputs = ander_in(f'{path}/ander.in', 'standard')
    inputs[tuning_var_name] = np.average(log_couplings(f'{path}/ander.log'))
    return inputs