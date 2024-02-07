from qim_functions import eff_ander_in, extract_level, pdiff
from run_functions import read_file
import numpy as np
import pandas as pd


def extract_ediff(find_edc_runs, fixed_var_name):
    values = read_file(f'{find_edc_runs}/var_completed.txt') #read the converged runs
    E_c = []
    for val in values:
        inputs = eff_ander_in(f'{find_edc_runs}/g={val}/last_runs','ed')
        # print(inputs['ed'])
        # ander_out = aextr(f'{find_edc_runs}/g={val}/last_runs/max.out', 3.0, 'all')
        if inputs['g']>1:
            loc_gound_state = extract_level(f'{find_edc_runs}/{fixed_var_name}={val}/last_runs/max.out', [1,0,0], 'all')
            # display(loc_gound_state)
            def crit_e(data_frame):
                E = data_frame['energy'].to_numpy()
                N = data_frame['n'].to_numpy()
                #Find the location of the critical iteration: Serves as the lower bound for the asymptotic regime
                i = np.argmin(np.abs(np.diff(E)))
                nc = N[i]
                ec = E[i]
                return ec
            E_c.append(crit_e(loc_gound_state))

    ec = round(np.average(E_c),8)
    ec_error = round(pdiff(np.min(E_c), np.max(E_c)),5)
    return ec, ec_error