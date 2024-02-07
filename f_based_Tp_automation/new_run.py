import os
import pickle
import numpy as np
from run_functions import launch_slurm_script
from qim_functions import create, worker
from .new_run_helpers import write_in, write_slurm_script, init_run_dir
from functools import partial
import json
import multiprocessing
import inspect



def step(var_count, fixed_var_value, run_direc, nb, s, r, run_index, fixed_var_name, params):#, fixed_var_name, nb, params, run_index):
# def step(var_count, fixed_var_value, **kwargs):
    run_path = f'{run_direc}/{fixed_var_name}={var_count}' #location of the run directory
    os.system(f'rm -rf {run_path}') #delete existing instance of the run directory
    title = f's={s}/nb={nb}/{run_index}-{var_count}' #title for the slurm script
    init_run_dir(run_path, nb, s, r) #initialize the run directory
    run_time = '24:00:00' #run time for the slurm script
    write_slurm_script(title,run_path, run_time) #write the slurm script
    params[fixed_var_name] = fixed_var_value #set the value of the fixed variable
    write_in(f'{run_path}/ander.in', **params) #write the ander.in file
    job_id = launch_slurm_script(run_path) #launch the slurm script
    # print(f'{fixed_var_name} = {fixed_var_value} [{var_count}]') #print the progress
    return job_id


def start_new_batch(run_direc:str, misc_dict:dict, inputs:dict, fixed_var_bounds:list, tuning_var_bounds:list) -> None:
    '''creates a directory with ander, ander.band/bath and ander.data files
    args:
        run_direc: directory for the run
        misc_dict: contains values of nb, run_index, s, fixed_var_name, tuning_var_name, num_runs
        inputs: contains values of U, g, K, drepos, dreneg'''
    s = misc_dict['s']; nb = misc_dict['nb']; r = None; run_index = misc_dict['run_index']
    fixed_var_name = misc_dict['fixed_var_name']; tuning_var_name = misc_dict['tuning_var_name']
    create(run_direc)
    with open(f'{run_direc}/.variable_names', 'w') as f:
        f.write(f'fixed_var_name = {fixed_var_name}\n')
        f.write(f'tuning_var_name = {tuning_var_name}')

    num_runs = misc_dict['num_runs']
    inputs['var_min'] = np.min(tuning_var_bounds); inputs['var_max'] = np.max(tuning_var_bounds)
    inputs[tuning_var_name] = 0.5*(inputs['var_min']+inputs['var_max'])
    assert len(fixed_var_bounds) == 2, 'fixed_var_bounds must be a list of length 2'
    assert len(tuning_var_bounds) == 2, 'tuning_var_bounds must be a list of length 2'
    d = (np.max(fixed_var_bounds) - np.min(fixed_var_bounds))/(num_runs+1)
    fixed_var_values = np.min(fixed_var_bounds) + d*np.arange(1, num_runs+1)
    fixed_var_values = np.round(fixed_var_values, 8)
    ander_in_params = {key:inputs[key] for key in ['U', 'g', 'K', 'drepos', 'dreneg', tuning_var_name, 'var_min', 'var_max']}
    results = []
    func = partial(step, run_direc=run_direc, nb=nb, s=s, r=None, run_index=run_index, fixed_var_name=fixed_var_name, params=ander_in_params)
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        for result in pool.imap(worker, [((var_count, var_value), func) for var_count, var_value in enumerate(fixed_var_values)]):
            results.append(result)
    runs_dic = {val:job_id for val, job_id in enumerate(results)}
    #save the runs_dic to a json file
    with open(f'{run_direc}/.runs_dic.json', 'w') as f:
        json.dump(runs_dic, f)

    










