import pandas as pd
import numpy as np
from plot_functions  import plot_t_star
from qim_functions import aextr, create, read_file, eff_ander_in, parallel
from .step3_plot_helper import phase_string, run_n_max, plot_driver_spectrum, write_title


def plot_all_runs(fixed_var_name, tuning_var_name, path_blue, out_direc, par, s, nb, num_cpu_plot):
    '''Plot all the runs in the path_blue folder and save them in out_direc. Also plots the T_star convergence.
    args: fixed_var_name (str), tuning_var_name (str), 
           path_blue (str): location of the runs, out_direc (str): location to save the images, 
        par (str): what iterations to plot, s (float): value of the bosonic bath exponent.
    '''
    create(out_direc)
    plot_t_star(path_blue, fixed_var_name, tuning_var_name).savefig(f'{out_direc}/t_star_convg.jpeg', dpi=300)
    converged_runs = read_file(f'{path_blue}/var_completed.txt')
    N_max = run_n_max(path_blue, fixed_var_name, converged_runs)
    Name = phase_string(tuning_var_name)
    for phase in ['min', 'max']:
        create(f'{out_direc}/{Name[phase]}')
    for phase in ['min', 'max']:
        create(f'{out_direc}/{Name[phase]}')
    
    in_args = []
    for index, fixed_var_val in enumerate(converged_runs):#read the effective inputs
        inputs = eff_ander_in(f'{path_blue}/{fixed_var_name}={fixed_var_val}/last_runs', tuning_var_name)
        #construct the value tuple
        value_tuple = (fixed_var_name, index, fixed_var_val, tuning_var_name)
        title_misc = f'$n_b={nb}$ [{fixed_var_val}]'
        for ph_ind, phase in enumerate(['min', 'max']):
            n_max = N_max[str(ph_ind+1)]
            in_path = f'{path_blue}'
            args = (in_path, inputs, phase, value_tuple, out_direc, title_misc, par, tuning_var_name,  s, n_max)
            in_args.append(args)
    parallel(plot_run, in_args, num_processes=num_cpu_plot)
    print(f'plotted {len(in_args)} find_edc_runs')
    return


def plot_run(in_path, inputs, phase, value_tuple, out_direc, title_misc, par,tuning_var_name, s, n_max):
    '''Plots a levels of single spectrum of a given phase
    args: in_path (str): location of the run directory, phase (str): phase of the run, 
        inputs (dic): effective inputs of the run,
        value_tuple (tuple): (fixed_var_name, ind, fixed_var_val, tuning_var_name), out_direc (str): location of Loc/Deloc plot folders,
        title_misc (str): misc. info to be added to the title, par (str): parity of the run, s (float): value of the band exponent,
        n_max (int): maximum of the x_axis in the plot
    returns: None
    '''
    (fixed_var_name, ind, fixed_var_val, tuning_var_name) = value_tuple
    #read the outputs
    try:
        spectrum = aextr(f'{in_path}/{fixed_var_name}={fixed_var_val}/last_runs/{phase}.out', 5.0, par)
    except:
        print(f'Error in reading {in_path}/{fixed_var_name}={fixed_var_val}/last_runs/{phase}.out')

    #construct the title of the plot:
    title = write_title(inputs, phase, tuning_var_name, title_misc, s)
    

    #construct the path to save the plot:
    Name = phase_string(tuning_var_name)
    save_dir = f'{out_direc}/{Name[phase]}'
    # create(save_dir)
    out_path = f'{save_dir}/{ind}_{fixed_var_val}.jpeg'

    #plot and save the spectrum
    plot_driver_spectrum(spectrum, title, inputs, n_max, out_path, s)
    return

