import pandas as pd
from qim_functions import extract_excite, pdiff
import os
import numpy as np


def rename_out(n_max:int, run_dir:str):
    '''renames the last ander.out file in the run_dir to ander.out{n_max}'''
    if os.path.exists(fr'{run_dir}/ander.out'):
        os.rename(fr'{run_dir}/ander.out', fr'{run_dir}/ander.out{str(n_max).zfill(2)}')
    return


def obtain_last_runs(run_dir:str, k:int=5) -> (bool,list):
    '''returns a list of k run_indices closest to the critical point'''
    ander_log = fr'{run_dir}/ander.log'
    with open(ander_log, 'r') as f:
        all_lines = f.readlines()
    run_id = []
    for line in all_lines:
        strip_line = line.strip()
        if '>' in strip_line:
            run_id.append((int(strip_line.split('>')[0]), int(strip_line[-1])))
    run_ids = pd.DataFrame(run_id, columns=['run_index', 'phase'])
    if np.all([phase in run_ids['phase'].to_numpy(int) for phase in [1, 2]]):#both phases are present
        status = True
    else:
        status = False
    n_max = run_ids['run_index'].max()
    rename_out(n_max, run_dir)
    indices = [index_array[i] for phase in [1, 2] for index_array in [run_ids[run_ids['phase'] == phase].sort_values('run_index', ascending=False)['run_index'].to_numpy(int)] for i in range(k)]
    return status, indices



def obtain_thresholds(run_dir:str) -> tuple:
    '''returns the lower and upper bounds on the critical energy by analyzing the runs in run_dir'''
    critical_energies = []
    status, indices = obtain_last_runs(run_dir, 3)

    if status:
        for ind in indices:
            ind_str =  str(ind).zfill(2)#''#
            ander_out = fr'{run_dir}/ander.out{ind_str}'
            driver_level = extract_excite(ander_out).rename(columns={'excite':'energy'})
            y = driver_level['energy']
            if len(y)> 5:
                avg_diff = [np.abs(pdiff(y[:-1], y[1:]))[i-1:i+2].mean() for i in range(1, len(y)-1)]
                ind_min = np.argmin(avg_diff)+1
                diff = avg_diff[ind_min-1] 
                energy = np.average(driver_level.loc[ind_min-1:ind_min+2,'energy'])
                if diff<1.0: #select levels that are coverged to within 1 percent
                    critical_energies.append(energy)
        # if np.all(driver_level['n'].to_numpy(int)%2 == 0) or np.all(driver_level['n'].to_numpy(int)%2 == 1):
        #     p = 1
        # else:
        p = 0.5
        low = round(np.average(critical_energies)*(1-p/100), 4)
        high = round(np.average(critical_energies)*(1+p/100),4)
        print(low, high, 100*(np.max(critical_energies)-np.min(critical_energies))/np.average(critical_energies))
        return (low, high)
    else:
        return (status, status)








