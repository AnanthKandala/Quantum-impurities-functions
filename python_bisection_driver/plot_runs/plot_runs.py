from qim_functions import create, parallel
from run_functions import obtain_variable_values
from .plot_runs_helpers import plot_run, get_last_runs
from ..qim_functions.ander_in_funcs import eff_ander_in 
from ..qim_functions.misc_funcs import obtain_names
import os
import multiprocessing
import numpy as np

def plot_driver_runs(runs_directory, out_direc, s, title_misc, nb=None):

    if multiprocessing.cpu_count() > 64: #running on the compute nodes
        parallel_status = False
    else:
        parallel_status = True        
    create(out_direc)
    os.system(fr'rm -rf {out_direc}/*')
    fixed_var_name, tuning_var_name = obtain_names(runs_directory)
    _, fixed_var_values = obtain_variable_values(runs_directory)
    in_args = []
    plot_count = 0
    for fixed_var_value in fixed_var_values:
        path = f'{runs_directory}/{fixed_var_name}={fixed_var_value}'
        ander_log = f'{path}/ander.log'
        if os.path.isfile(ander_log):
            last_runs = get_last_runs(ander_log)
            if len(last_runs) == 2:
                inputs = eff_ander_in(f'{path}', tuning_var_name)
                value_tuple = (plot_count, tuning_var_name)
                for phase, run_index in last_runs.items():
                    if parallel_status:
                        in_args.append((path, run_index, inputs, phase, value_tuple, out_direc, title_misc, s, nb))
                    else:
                        plot_run(path, run_index, inputs, phase, value_tuple, out_direc, title_misc, s, nb)
                                  # run_direc, run_index, inputs, phase, value_tuple, out_direc, title_misc, s
            plot_count += 1

    print(f'plotting {len(in_args)} runs')
    if parallel_status:
        parallel(plot_run, in_args)
    return

def plot_temp_runs(runs_directory:str, out_direc:str, s:float, title_misc:str, nb=None):
    # create(out_direc)
    # os.system(fr'rm -rf {out_direc}/*')
    fixed_var_name, tuning_var_name = obtain_names(runs_directory)
    _, fixed_var_values = obtain_variable_values(runs_directory)
    in_args = []
    plot_count = 0
    for fixed_var_value in fixed_var_values:
        path = f'{runs_directory}/{fixed_var_name}={fixed_var_value}'
        ander_log = f'{path}/ander.log'
        if os.path.isfile(ander_log):
            last_runs = get_last_runs(ander_log)
            if len(last_runs) == 2:
                inputs = eff_ander_in(f'{path}', tuning_var_name)
                value_tuple = (plot_count, tuning_var_name)
                for phase, run_index in last_runs.items():
                        in_args.append((path, run_index, inputs, phase, value_tuple, out_direc, title_misc, s, nb))
                                  # run_direc, run_index, inputs, phase, value_tuple, out_direc, title_misc, s
            plot_count += 1
    print(f'plotting {len(in_args)} runs')
    if len(in_args) > 0:
        count = 0
        while count < 10:
            try:
                parallel(plot_run, in_args)
                break
            except Exception as e:
                if 'not a png file' in str(e).lower():
                    count += 1
                    print(e)
                    print(f'Plotting failed. Trying again. Attempt {count}')
                else:
                    raise e
    return

