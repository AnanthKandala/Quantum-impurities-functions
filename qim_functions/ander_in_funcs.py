import numpy as np
from .log_funcs import log_couplings 


#Functions to process the ander.in file
def ander_in(infile, driver):
    '''
    Extracts the parameters from the ander.in file and returns them as a dictionary.
    parameters = {
            'ed': ed,
            'U': U,
            'eta': eta,
            'Gamma': Gamma,
            'delta': delta,
            'g': g,
            'K': K,
            'h': h,
            'lower_threshold': lower_threshold,
            'upper_threshold': upper_threshold,
            'iexcdr': iexcdr,
        }
    '''
    with open(infile, "r") as ff:
            Aa = ff.readlines()
    if driver == 'standard':
        n0 = 0
    else:
        n0 = 2

    Bb = Aa[n0].split()
    ed = Bb[0]
    U = Bb[1]
    Gamma = Bb[2]
    c = Aa[1][2].split()
    if float(U) != 0.0:
        eta = (2.0 * float(ed) / float(U)) + 1
    else:
        eta = np.inf
    delta = float(Aa[n0 + 3].split()[0])
    h = float(Aa[n0 + 3].split()[1])
    g = float(Aa[n0 + 1].split()[2])
    K = int(Aa[n0 + 5].split()[3])
    parameters = {
        'ed': ed,
        'U': U,
        'eta': eta,
        'Gamma': Gamma,
        'delta': delta,
        'h': h,
        'g': g,
        'K': K
    }

    if n0==2:
        lower_threshold = Aa[1].split()[2]
        upper_threshold = Aa[1].split()[3]
        iexcdr = Aa[1].split()[1]
        parameters['lower_threshold'] = lower_threshold
        parameters['upper_threshold'] = upper_threshold
        parameters['iexcdr'] = int(iexcdr)
    return parameters


def eff_ander_in(path, tuning_var_name):
    '''
    finds the inputs params and replaces the tuning variable with its critical value from the log file
    args: path (str): location of the ander.in and ander.log files
    returns: dict: dictionary of the input parameters
    '''
    assert tuning_var_name in ['ed', 'U', 'Gamma', 'delta', 'h', 'g'], 'tuning_var_name must be one of ed, U, Gamma, delta, h, g, K'
    inputs = ander_in(f'{path}/ander.in', 'find_driver')
    crit_value = np.mean(log_couplings(f'{path}/ander.log'), dtype=np.float64)
    inputs[tuning_var_name] = crit_value
    if tuning_var_name == 'ed':
        U = float(inputs['U'])
        ed = float(inputs['ed'])
        if U != 0.0:
            eta = (2.0*ed/U) + 1
        else:
            eta = np.inf
        inputs['eta'] = eta
    return inputs




