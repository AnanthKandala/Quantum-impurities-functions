import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc,rcParams
rc('text', usetex=True)
rc('font', weight='bold')
custom_preamble = {
    "text.latex.preamble":
        r"\usepackage{amsmath,amssymb}" # for the align, center,... environment
        ,
    }
plt.rcParams.update(custom_preamble)
import os
from qim_functions import aextr, free_boson_energy, pdiff, create, ph_sym_spect
import re
from python_bisection_driver.run_functions.calculate_phase import check_degeneracy


def plot_run(run_direc, run_index, inputs, phase, value_tuple, out_direc, title_misc, s, nb=None):
    '''Plots a levels of single spectrum of a given phase
    args: in_path (str): location of the run directory, phase (str): phase of the run, 
        inputs (dic): effective inputs of the run,
        value_tuple (tuple): (fixed_var_name, ind, fixed_var_val, tuning_var_name), out_direc (str): location of Loc/Deloc plot folders,
        title_misc (str): misc. info to be added to the title, par (str): parity of the run, s (float): value of the band exponent,
        n_max (int): maximum of the x_axis in the plot
    returns: None
    '''
    (ind, tuning_var_name) = value_tuple
    spectrum = aextr(f'{run_direc}/ander.out{run_index}', 5.0, 'all') #extract the spectrum from ander.out file
    log_file = f'{run_direc}/ander.log'
    log_frame = pd.read_csv(log_file,sep=r'\s+')
    diff = log_frame.iloc[-1]['diff']
    title_misc += f', convg_{{diff}}$={diff}$'
    title = write_title(inputs, tuning_var_name, title_misc, s) #write the title of the plot
    #construct the path to save the plot:
    save_dir = f'{out_direc}/{phase}'
    create(save_dir)
    outpath = f'{save_dir}/{ind}_{os.path.basename(run_direc)}.jpeg'
    #plot and save the spectrum
    plot_driver_spectrum(spectrum, title, phase, outpath, s, nb)
    return

    

def plot_driver_spectrum(spectrum, title, phase, outpath, s, nb=None):
    '''plots the spectrum of a driver run and saves it to outpath.
    args: spectrum (pd.DataFrame): spectrum of the driver run,
          title (str): title of the plot,
          inputs (dict): inputs to the driver run,
          n2 (int): x_axis lim,
          outpath (str): path to save the plot
          eb (float): free bosonic energy
    returns: None'''
    # print(f'plotting {outpath}')
    fig, ax = plt.subplots(dpi=300)
    #setting figure parameters.
    ax.set_ylabel(r'$E$')
    ax.set_xlabel(r'$N$')
    emax = 3.0
    ymax = emax
    ymin = -0.01
    ax.set_ylim(ymin, ymax)
    y_ticks = np.arange(0.0, ymax+0.5,0.5)
    ax.set_yticks(y_ticks)
    n1 = 0 #int(np.min(A[:,0]))
    ms = 1
    lw = 0.4
    nmax = spectrum['n'].max()
    x_ticks = range(n1, nmax+2,2)
    ax.set_xticks(x_ticks)
    ax.set_xlim(n1, nmax)
    
    #plotting legend
    # marker = {-1:'o', 0:'s', 1:'x'} #jf_values -> marker for the level
    # name = {-1:'P', 0:'B', 1:'H'} #jf_values -> label in the legend
    # color = {-1:'blue', 0:'red', 1: 'green'} #jf_value -> color of the level

    marker = {-1:'', 0:'s', 1:''} #jf_values -> marker for the level
    name = {-1:'P', 0:'B', 1:'H'} #jf_values -> label in the legend
    color = {-1:'green', 0:'red', 1: 'green'} #jf_value -> color of the level
    

    #plotting free bosonic energies
    e1 = free_boson_energy(s)
    while e1<=emax:
        ax.axhline(e1,linewidth=0.5,linestyle='dashed',color='b')
        e1 += free_boson_energy(s)
      
    plotted_jf = []
    N_crit = []
    E_crit = []
    for ind, qno in spectrum.iterrows():
        sf = qno['sf']
        jf = qno['jf']
        index = qno['index']
        condition = (spectrum['sf'] == sf) & (spectrum['jf'] == jf) & (spectrum['index'] == index)
        level = spectrum[condition]
        N = level['n'].to_numpy(dtype=np.float64)
        E = level['energy'].to_numpy(dtype=np.float64)
        level_type = int(jf)
        if level_type in marker:
            ax.plot(N, E, color=color[level_type], markersize=ms, marker=marker[level_type], lw=lw, alpha=0.1)
        else:
            ax.plot(N, E, color='green', markersize=ms, marker='.', lw=lw, alpha=0.1)

        if level_type not in plotted_jf:
            plotted_jf.append(level_type)
        
        E_select = E[np.where(E<emax)]
        if len(E_select) > 2 and np.any(E_select<emax):
            arg = np.argmin(np.abs(np.diff(E_select)))
            n_min ,e_crit = N[arg], E[arg]
            # ax.axhline(e_crit, lw=0.2, color='r')
            # ax.axvline(n_min, lw=0.2, color='r')
            E_crit.append(e_crit)
            N_crit.append(n_min)
    ax.scatter(N_crit, E_crit, marker='o', facecolors='none', edgecolors='black', s = ms+2)

    #iteration that was used to analyze the phase:
    free_bosons = np.array([i*free_boson_energy(s) for i in range(6)])
    n_levels = len(free_bosons)
    iterations = np.unique(spectrum['n'].to_numpy())
    error = np.empty(len(iterations))
    for i, n in enumerate(iterations):
        energies = spectrum.query(f'n=={n}')['energy'].to_numpy()[:n_levels]
        error[i] = np.average(np.abs(pdiff(energies, free_bosons))) + check_degeneracy(n, spectrum)
    min_error = np.min(error)
    if min_error == 0:
        min_error = -np.inf
    else:
        min_error = round(math.log10(np.min(error)), 3)
    n_stable = iterations[np.argmin(error)]
    ax.axvline(n_stable, lw=0.2, color='r')
    ax.set_title(title+'\n'+fr'phase-check: $n={n_stable}, tol={min_error} $ {phase}')
    # for key, level in name.items():
    #     if key in plotted_jf:            
    #         ax.plot([], [], lw=0,color=color[key], markersize=ms, marker=marker[key], label=fr'${key}$')
    if nb is not None:
        #plot the ph symmetric levels
        ph_energies = ph_sym_spect(s, nb, 200)['energy'].to_numpy()
        for e in ph_energies:
            ax.axhline(e, lw=0.1, color='k')
    fig.tight_layout()
    fig.savefig(outpath, dpi=300)
    plt.close(fig)
    return 


def write_title(inputs, tuning_var_name, title_misc, s):
    '''write the title of the plot:
    args: inputs (dict) --> dictionary of inputs, phase (str) --> phase name, tuning_var_name (str) --> name of the tuning variable,
          fixed_var_name (str) --> name of the fixed variable, fixed_var_val (float) --> value of the fixed variable,
          title_misc (str) --> misc. info to be added to the title, s (float) --> value of the band exponent
    returns: title (str) --> title of the plot
    '''
    
    keys = ['K', 'U', 'g', 'ed', 'eta', 'Gamma']
    latex_dict = {
        'K': r'K',
        'U': r'U',
        'g': r'g',
        'ed': fr'\varepsilon_{{d}}',
        'Gamma': fr'\Gamma',
        'eta': fr'\eta'
    }            
    if tuning_var_name == 'ed':
        keys.remove('eta')
    string_dict = {}
    for key in keys:
        if key == tuning_var_name: #add _c if the key is the tuning variable
            if tuning_var_name == 'ed': #add \varepsilon_dc if the tuning variable is ed
                string_dict['ed'] = fr"$\varepsilon_{{dc}}={inputs['ed']:.12f}$"
                string_dict['eta'] = fr"$\eta_{{c}} = {inputs['eta']:.8f}$"
            else:
                string_dict[key] = fr"${latex_dict[tuning_var_name]}_c={inputs[tuning_var_name]:.12f}$"
        elif key=='K':
            string_dict[key] = fr"${latex_dict[key]}={int(inputs[key])}$"
        else: #add to the title if it is a fixed variable
            string_dict[key] = fr"${latex_dict[key]}={round(float(inputs[key]), 8)}$"
    str1 = ', '.join([string_dict[key] for key in ['K', 'U', 'g', 'eta']])
    str2 = ', '.join([string_dict[key] for key in ['ed','Gamma']])
    title_string = fr'\noindent $s={s}$, {str1}, \newline {str2}, {title_misc}'
    return title_string



def get_last_runs(log_file):
    log_frame = pd.read_csv(log_file,sep=r'\s+')
    phases = log_frame['phase'].unique()
    num_phases = len(phases)
    phase_boundary = {}
    if num_phases == 0:
        return phase_boundary
    else:
        for phase in phases:
            phase_boundary[phase] = log_frame[log_frame['phase']==phase].iloc[-1]['run_index']
        return phase_boundary