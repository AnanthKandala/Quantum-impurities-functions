import pandas as pd
import numpy as np
from .log_convg import plot_t_star
from qim_functions import create, eff_ander_in, parallel, obtain_names, worker
from .plot_find_runs_helper import plot_run, run_n_max, phase_string
from run_functions import run_check_func
import os
import multiprocessing

def plot_all_runs(path_blue, out_direc, par, s, title_misc, extra_iterations=None):
    '''Plot all the runs in the path_blue folder and save them in out_direc. Also plots the T_star convergence.
    args: 
        fixed_var_name (str), tuning_var_name (str), 
        path_blue (str): location of the runs, out_direc (str): location to save the images, 
        par (str): what iterations to plot, s (float): value of the bosonic bath exponent.
        extra_iterations (list): list of tuple that contain the iterations to be identified on the plot
    '''
    fixed_var_name, tuning_var_name = obtain_names(path_blue).values()
    create(out_direc)
    os.system(fr'rm -rf {out_direc}/*')
    competed_runs = run_check_func(path_blue)
    if len(competed_runs) == 0:
        print(f'No completed runs found in {path_blue}. Exiting.')
        return
    else:
        plot_t_star(path_blue,tuning_var_name).savefig(f'{out_direc}/t_star_convg.jpeg', dpi=300)
        converged_runs = pd.read_csv(fr'{path_blue}/completed_couplings.txt', sep=r'\s+')
        in_paths = [f'{path_blue}/{run_path}' for run_path in converged_runs['index']]
        N_max = run_n_max(in_paths)
        Name = phase_string(tuning_var_name)
        for phase in ['min', 'max']:
            create(f'{out_direc}/{Name[phase]}')
        for phase in ['min', 'max']:
            create(f'{out_direc}/{Name[phase]}')
        
        in_args = []
        for index, run_path in enumerate(in_paths):#read the effective inputs
            inputs = eff_ander_in(f'{run_path}/last_runs', tuning_var_name)
            #construct the value tuple
            value_tuple = (index, tuning_var_name)
            for ph_ind, phase in enumerate(['min', 'max']):
                # title_misc = f'[{Name[phase]}] run{run_value} - [{fixed_var_val}]' #phase and run index
                n_max = N_max[str(ph_ind+1)] #maximum of the x_axis in the plot
                if extra_iterations is None:
                    args = (run_path, inputs, phase, value_tuple, out_direc, title_misc, par, tuning_var_name, s, n_max)
                else:
                    args = (run_path, inputs, phase, value_tuple, out_direc, title_misc, par, tuning_var_name, s, n_max, extra_iterations[index])
                in_args.append(args)
        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        pool.starmap(plot_run, in_args)
        pool.close()
        pool.join()
    return


