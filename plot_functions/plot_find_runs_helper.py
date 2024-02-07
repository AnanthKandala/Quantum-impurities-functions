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
from qim_functions import aextr, free_boson_energy



def plot_run(in_path, inputs, phase, value_tuple, out_direc, title_misc, par,tuning_var_name, s, n_max, extra_iterations=None):
    '''Plots a levels of single spectrum of a given phase
    args: in_path (str): location of the run directory, phase (str): phase of the run, 
        inputs (dic): effective inputs of the run,
        value_tuple (tuple): (fixed_var_name, ind, fixed_var_val, tuning_var_name), out_direc (str): location of Loc/Deloc plot folders,
        title_misc (str): misc. info to be added to the title, par (str): parity of the run, s (float): value of the band exponent,
        n_max (int): maximum of the x_axis in the plot
        extra_iterations (list): list of iterations to be identified on the plot
    returns: None
    '''
    (ind, tuning_var_name) = value_tuple
    run_dir = os.path.basename(in_path)
    #read the outputs
    try:
        spectrum = aextr(f'{in_path}/last_runs/{phase}.out', 5.0, par)
    except:
        print(f'Error in reading {in_path}/last_runs/{phase}.out')

    #construct the title of the plot:
    title = write_title(inputs, tuning_var_name, title_misc, s)
    

    #construct the path to save the plot:
    Name = phase_string(tuning_var_name)
    save_dir = f'{out_direc}/{Name[phase]}'
    out_path = f'{save_dir}/{ind}_{run_dir}.jpeg'

    #plot and save the spectrum
    plot_driver_spectrum(spectrum, title, inputs, par, n_max, out_path, free_boson_energy(s), extra_iterations)
    # print(f'plotted {out_path}')
    return

    

def plot_driver_spectrum(spectrum, title, inputs, par, n2, outpath, eb, extra_iterations):
    '''plots the spectrum of a driver run and saves it to outpath.
    args: spectrum (pd.DataFrame): spectrum of the driver run,
          title (str): title of the plot,
          inputs (dict): inputs to the driver run,
          n2 (int): x_axis lim,
          outpath (str): path to save the plot
          eb (float): free bosonic energy
    returns: None'''
    count = 0
    while count < 10:
        try:
            fig, ax = plt.subplots(dpi=300)
            #setting figure parameters.
            ax.set_title(title)
            ax.set_ylabel(r'$E$')
            ax.set_xlabel(r'$N$')
            emax = 3.0
            ax.set_ylim(-0.01, emax)
            y_ticks = np.arange(0.0, emax+0.5,0.5)
            ax.set_yticks(y_ticks)
            if par=='odd':
                n1 = 1 #int(np.min(A[:,0]))
            else:
                n1 = 0
            ms = 1
            lw = 0.4
            x_ticks = range(n1,n2+2,2)
            ax.set_xticks(x_ticks)
            x_ticks = np.arange(n1,n2+4,4)
            ax.set_xlim(n1, n2)
            
            #plotting legend
            # marker = {-1:'o', 0:'s', 1:'x'} #jf_values -> marker for the level
            # name = {-1:'P', 0:'B', 1:'H'} #jf_values -> label in the legend
            # color = {-1:'blue', 0:'red', 1: 'green'} #jf_value -> color of the level

            marker = {-1:'', 0:'s', 1:''} #jf_values -> marker for the level
            name = {-1:'P', 0:'B', 1:'H'} #jf_values -> label in the legend
            color = {-1:'green', 0:'red', 1: 'green'} #jf_value -> color of the level
            

            #plotting free bosonic energies
            e1 = eb
            while e1<=emax:
                ax.axhline(e1,linewidth=0.5,linestyle='dashed',color='b')
                e1+=eb
            
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

            # for key, level in name.items():
            #     if key in plotted_jf:            
            #         ax.plot([], [], lw=0,color=color[key], markersize=ms, marker=marker[key], label=fr'${key}$')
            if extra_iterations is not None:
                for N_extra in extra_iterations:
                    ax.axvline(N_extra, lw=0.2, color='b')
            #plotting the thresholds used in the find_driver
            if 'lower_threshold' in inputs:
                for e in [inputs['lower_threshold'], inputs['upper_threshold']]:
                    ax.axhline(float(e), lw=lw/2, color='k')
            # ax.legend(loc=0, fontsize='x-small', title=r'$j_f$')
            fig.tight_layout()
            fig.savefig(outpath, dpi=300, format='png')
            plt.close(fig)
            break
        except:
            print(f'Error in plotting {outpath}')
            count += 1
            print(f'Plotting failed. Trying again. Attempt {count}')
    return

def phase_string(var):
    '''
    converts 'max/min' to 'Loc/Deloc' for each var
    args: var (str): name of the tuning variable
    returns: Name (dic): maps {max, min} to {Loc, Deloc}
    '''
    Name = {}
    if var in ['g', 'ed']:
        Name['max'] = 'Loc'
        Name['min'] = 'Deloc'
    elif var in ['Gamma']:
        Name['max'] = 'Deloc'
        Name['min'] = 'Loc'
    return Name



def run_n_max(directories):
    '''extract the maximum possible N from all the runs in path
    args: path (str): location of the runs, fixed_var_name (str): name of the fixed variable, 
              values (list): list of values of the fixed variable
    returns: N_max (dict): phase_status (dic): {'ph': [boolean, n_max]} for ph in [1,2]'''

    def max_n(infile):
        '''
        extracts the maximum number of iterations from the ander.log file
        args: infile (str): location of the log file
        returns: phase_status (dic): {'ph': [boolean, n_max]} for ph in [1,2]
        '''
        f = open(infile, "r")
        all_lines = f.readlines()
        phase_status = {'1':[False,0], '2':[False,0]}
        for line in all_lines[::-1]:
            if '>' in line:
                split_line = line.split()
                phase = split_line[-1].rstrip('\n')
                if phase in phase_status.keys():
                    if not phase_status[phase][0]:
                        phase_status[phase][0] = True
                        phase_status[phase][1] = int(split_line[3])  #one of the phases has been found
                if phase_status['1'][0] and phase_status['2'][0]:
                    break
        return phase_status

    N_max = {'1':0, '2':0}
    for dir in directories:
        path = f'{dir}/last_runs/ander.log'
        phase_state = max_n(path)
        for i in ['1', '2']:
            if phase_state[i][1]>N_max[i]:
                N_max[i] = phase_state[i][1]
    return N_max


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
    title_string = fr'\noindent {str1}, \newline {str2}, {title_misc}'
    return title_string