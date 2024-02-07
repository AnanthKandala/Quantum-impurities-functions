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
from qim_functions import free_boson_energy
import itertools
import matplotlib.colors as mcolors

def cont_color(n,nmax, cmap=plt.cm.jet):
    '''Maps the number n to a normalized continuous color gradient from 0 to nmax
    args: n(int): number to be mapped, nmax(int): maximum number to be mapped
    returns: color(tuple): tuple of rgb values'''
    norm = plt.Normalize(vmin=0, vmax=nmax)
    return cmap(norm(n))

def gen_plot_els(plot_vars, lw=1, ms=2) -> list:
    '''generates cyclic markers and colors for the plot given an input of a cerain length'''
    n = len(plot_vars)
    markers = itertools.cycle(['^', 'v', '.', 's',  'D', 'p', '+', 'x', 'o', '1', '2', '3', '4', '8', 'h', 'H', 'd'])
    linestyles = itertools.cycle(['-', '--', '-.', ':'])
    colors = itertools.cycle(list(mcolors.TABLEAU_COLORS.values()))
    return_plot_els = [{'marker':next(markers), 'color':next(colors), 'linestyle':next(linestyles), 'lw':lw, 'ms':ms} for i in range(n)]
    return return_plot_els


def plot_spectrum(spectrum, title, n2, outpath, s):
    '''plots the spectrum of a run and saves it to outpath.
    args: spectrum (pd.DataFrame): spectrum of the driver run,
          title (str): title of the plot,
          inputs (dict): inputs to the driver run,
          n2 (int): x_axis lim,
          outpath (str): path to save the plot
    returns: None'''
    fig, ax = plt.subplots(dpi=300)
    #setting figure parameters.
    ax.set_title(title)
    ax.set_ylabel(r'$E$')
    ax.set_xlabel(r'$N$')
    emax = 3.0
    ax.set_ylim(0.0,emax)
    n1 = 0 #int(np.min(A[:,0]))
    ms = 1
    lw = 0.5
    x_ticks = range(n1,n2+2,2)
    ax.set_xticks(x_ticks)
    x_ticks = np.arange(n1,n2+4,4)
    ax.set_xlim(n1, n2)
    
    #plotting legend
    marker = {-1:'o', 0:'s', 1:'x', 2:'.', -2:'.', 'none':'.'} #jf_values -> marker for the level
    name = {-1:'P', 0:'B', 1:'H',2:'D', -2:'D'} #jf_values -> label in the legend
    color = {-1:'blue', 0:'red', 1: 'green', 2:'yellow',-2:'yellow', 'none':'k'} #jf_value -> color of the level
    

    #plotting free bosonic energies
    eb = free_boson_energy(s)
    e1 = eb
    while e1<=emax:
        ax.axhline(e1,linewidth=0.3,linestyle='dashed',color='b')
        e1+=eb
    # X = np.linspace(0, 100, 30)

    # E_loc=np.array([0. , 0.49276093, 1.09327376, 1.80579008])+0.1853
    # for e in E_loc:
    #     ax.axhline(e,color='b',linestyle='dotted',linewidth=0.7)
        # 0  1   2   3   4
    #A = [N, E, sf, jf, ind]
      
    unique_qno = spectrum[['sf', 'jf', 'index']].drop_duplicates()
    plotted_jf = []
    N_crit = []
    E_crit = []
    for ind, qno in spectrum.iterrows():
        sf = qno['sf']
        jf = qno['jf']
        index = qno['index']
        condition = (spectrum['sf'] == sf) & (spectrum['jf'] == jf) & (spectrum['index'] == index)
        level = spectrum[condition]
        N = level['n'].to_numpy()
        E = level['energy'].to_numpy()
        level_type = int(jf)
        ax.plot(N, E, color=color[level_type], markersize=ms, marker=marker[level_type], lw=lw, alpha=0.1)

        if level_type not in plotted_jf:
            plotted_jf.append(level_type)
        
        E_select = E[np.where(E<emax)]
        N_select = N[np.where(E<emax)]
        
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
        
    # ax.legend(loc=0, fontsize='x-small', title=r'$j_f$')
    fig.tight_layout()
    fig.savefig(outpath, dpi=300)
    plt.close(fig)
    return 


'''
path_blue = r'/blue/physics-dept/an.kandala/Localf_model/s=0.6/find_Gamma_c/K=100_test_runs/run4' #location of the runs
path_0 = r'/orange/physics-dept/an.kandala/proper_research/model_with_local_fermion/s=0.6/p_h_asymmetric_boundary/K=100_tests/narrowing_critical_end_point' #location of the notebook
from defaults import *
# from mpl_toolkits.axes_grid1.inset_locator import inset_axes

fixed_var_name = 'eta'
tuning_var_name = 'Gamma'
path = f'{path_blue}/{fixed_var_name}=0/'
s = 0.6
inputs = ander_in(f'{path}/ander.in', 'find_driver')
    
    #obtain the critical coupling:
inputs[tuning_var_name] = np.mean(log_couplings(f'{path}/ander.log'), dtype=float)
for key in inputs:
    inputs[key] = float(inputs[key])

misc_string = f'first bosonic excitation'
#title for the plot:
title = fr"\noindent $s={s}, K={int(inputs['K'])}, U={inputs['U']}, g={inputs['g']}, \eta={inputs['eta']}$ \newline  $\epsilon_d={inputs['ed']}, \Gamma_c={inputs['Gamma']:.12f}$, {misc_string}"

#Read the log file and plot the 20 runs closest to the end point:
ander_log = f"{path}/ander.log"
f = open(ander_log, "r")
all_lines = f.readlines()
phase_status = {}
max_index = 0
count = 0
n_max = 0
for line in all_lines[::-1]:
    if count < 49:
        if '>' in line:
            split_line = line.split()
            phase = split_line[-1].rstrip('\n')
            run_index = split_line[0].split('>')[0]
            n_max = max(n_max, int(split_line[3]))
            if phase not in phase_status:
                phase_status[phase] = [run_index] 
            else:
                phase_status[phase].append(run_index)
            count += 1

fig, ax = plt.subplots(dpi=300)
#setting figure parameters.
ax.set_title(title)
ax.set_ylabel(r'$E$')
ax.set_xlabel(r'$N$')
n1 = 0 #int(np.min(A[:,0]))
n2 = n_max
ms = 1
lw = 0.5
x_ticks = range(n1,n2,2)
ax.set_xticks(x_ticks)
x_ticks = np.arange(n1,n2+4,4)
ax.set_xlim(n1, n2)

for e in [inputs['lower_threshold'], inputs['upper_threshold']]:
        ax.axhline(e, lw=lw/2, color='k')

color = {'1':'r', '2':'g', '-1':'b', '-2':'k'}
marker = {'1':'o', '2':'s', '-1':'x', '-2':'^'}
linestyle = {'1':':', '2':'--', '-1':'-.', '-2':'-.-'}
seen_key = []
for phase, run_indices in phase_status.items():
    for run_ind in run_indices:
        ander_out = f'{path}/ander.out{str(run_ind).zfill(2)}'
        level = extract_level(ander_out, [0,0,1], 'all') #extract the first bosonic exciation
        ax.plot(level['n'], level['energy'], lw=lw, color=color[phase], marker=marker[phase], markersize=ms)
        if phase not in seen_key:
            seen_key.append(phase)

for phase in seen_key:
    ax.plot([], [], lw=lw, color=color[phase], marker=marker[phase], markersize=ms, label=f'phase ${phase}$')

ax1 = ax.inset_axes([0.1, 0.15, 0.4, 0.3])
ms = 1 #markersize
Color = {1:'r', 2:'g'}
direc0 = path_blue
marker = '.'
t_star, g_star = extract_t_star(ander_log)
status = []
for phase in [1,2]:
    T = t_star[phase]
    G = g_star[phase]
    ax1.plot(np.log10(G), np.log10(np.abs(T)), lw=0.1, marker=marker, markersize=ms, color = Color[phase])        
ax1.set_ylabel(r'$\log T^*$')
ax1.set_xlabel('$\log|d\mathrm{' + f'{tuning_var_name}' +'}|$')
ax.legend(loc=0, fontsize='small')
fig.tight_layout()
outimage = f'{path_0}/test.jpeg'
fig.savefig(outimage, dpi=300)

'''