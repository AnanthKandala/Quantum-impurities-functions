import pandas as pd
import numpy as np
from qim_functions import eff_ander_in
from run_functions import process_run_dir
import os

def run_complete_check(run_path:str, fixed_var_name:str, tuning_var_name:str, num_runs:int):
    '''Checks if all the calculations are done for the run_path. If yes, returns the ed values for the completed runs.
    args:
        run_path: path to the directory containing the run directories.
        fixed_var_name: name of the variable that is fixed.
        tuning_var_name: name of the variable that is tuned by the find_driver.
        num_runs: number of fixed_var_values.
    returns:
        completed_runs: list of the corresponding indices.'''
    fixed_var_values = list(range(num_runs))
    status = True
    completed_runs = []
    for j, var_value in enumerate(fixed_var_values):
        direc = f'{run_path}/{fixed_var_name}={var_value}'
        file = f'{direc}/script_output'
        if os.path.isfile(file): #script_output file present
            if 'calculation complete!' not in open(file).read(): #calculation not complete.
                status = False
                break
            else: #calculation complete.
                # process_run_dir(direc)
                last_runs = f'{direc}/last_runs'
                if os.path.isdir(last_runs): #last_runs is present.
                    eff_in = eff_ander_in(last_runs, tuning_var_name)
                    completed_runs.append(var_value)
        else: #script_output not present. This should be because the calculation hasn't started yet.
            status = False
            break
    #status = True --> all the calculations are done
    #status = False --> some calculations are not done
    return status, completed_runs
