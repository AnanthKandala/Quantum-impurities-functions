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
from plot_functions import plot_t_star, write_title
from qim_functions import ander_in, log_couplings, extract_t_star, extract_excite
import os
import pandas as pd


def Tp_driver_check(path, tuning_var_name, outimage,s, nb, selected_ind=[]):
    '''Plots the variation of the level thats being tracked in the find driver on either side of the critical point. Also plot the variation of the T* vs dg from the log file.
    args: path(str)-->location of the run, fixed_var_name(str)-->name of the fixed variable, tuning_var_name(str)-->name of the tuning variable,
          outimage(str)-->location of the output image
    returns: None
    '''
    inputs = ander_in(f'{path}/ander.in', 'find_driver')
        #obtain the critical coupling:
    inputs[tuning_var_name] = np.mean(log_couplings(f'{path}/ander.log'), dtype=float)
    inputs = {key: float(item) for key, item in inputs.items()}
    misc_string = '$E[5]^2 - E[4]^2$'#iexcdr_deocder( inputs['iexcdr'])
    #title for the plot:
    title = write_title(inputs, tuning_var_name, misc_string, s)
    # title = fr"\noindent $K={int(inputs['K'])}, U={inputs['U']}, g={inputs['g']}, \eta={inputs['eta']}$ \newline  $\epsilon_d={inputs['ed']}, \Gamma_c={inputs['Gamma']}$, {misc_string}"

    #Read the log file and plot the 20 runs closest to the end point:
    ander_log = f"{path}/ander.log"
    f = open(ander_log, "r")
    all_lines = f.readlines()
    phase_status = {}
    count = 0
    n_max = 0
    for line in all_lines:
        if '>' in line:
            split_line = line.split()
            phase = split_line[-1].rstrip('\n')
            run_index = split_line[0].split('>')[0]
            n_max = max(n_max, int(split_line[3]))
            if phase not in phase_status:
                phase_status[phase] = [int(run_index)] 
            else:
                phase_status[phase].append(int(run_index))
            count += 1

    fig, ax = plt.subplots(dpi=180)
    #setting figure parameters.
    ax.set_title(title)
    ax.set_ylabel(r'Transformed $E_{diff}$')
    ax.set_xlabel(r'$N$')
   
    ms = 4
    lw = 0.3
    

    for e in [inputs['lower_threshold'], inputs['upper_threshold']]:
            ax.axhline(e, lw=lw/2, color='k')

    tracking_path = '/orange/physics-dept/an.kandala/proper_research/model_with_local_fermion/s=0.6/nb_check/automating_Tp/find_LC/Tp_autotracking.json'
    tracking = pd.read_json(tracking_path)
    #plot the expected values at BC and LC
    colors = {'LC':'r', 'BC':'b'}
    for e_type in ['LC', 'BC']:
        ax.axhline(tracking.iloc[nb-4][e_type], lw=lw/2, color=colors[e_type], label=f'${e_type}$', linestyle='--')

    colors = {'1':'r', '2':'g', '-1':'b', '-2':'k'}
    marker = {'1':'o', '2':'s', '-1':'x', '-2':'^'}
    linestyle = {'1':':', '2':'--', '-1':'-.', '-2':'-.-'}
    seen_key = []
    n_max = 0
    all_runs = [(phase0, r) for phase0, run_indices in phase_status.items() for r in run_indices]
    max_run_ind = np.max(np.array([pair[1] for pair in all_runs]).astype(int))
    if len(selected_ind)!=0:
        runs = [pair for pair in all_runs if pair[1] in selected_ind]
    else:
        runs = all_runs[::-1][:20]
    for phase0, run_ind in runs:
        if int(phase0)==9:
            continue
        if int(phase0)%2 == 0:
                phase = '2'
        elif int(phase0)%2 == 1:
            phase = '1'
        if phase in marker:
                if int(run_ind) == max_run_ind:
                    ander_out = f'{path}/ander.out{str(run_ind).zfill(2)}'
                    if os.path.exists(ander_out):
                        level = extract_excite(ander_out) #extract the level thats being tracked
                    else:
                        ander_out = f'{path}/ander.out'
                        level = extract_excite(ander_out) #extract the level thats being tracked
                else:
                    ander_out = f'{path}/ander.out{str(run_ind).zfill(2)}'
                    level = extract_excite(ander_out)   
                #lastit it should be Nan
                mask = level['fxsplit'].to_numpy(float)>0
                ax.plot(level['n'], level['excite'], lw=lw, color=colors[phase])
                ax.plot(level['n'][mask], level['excite'][mask], lw=0, color=colors[phase], marker='X', markersize=ms)
                ax.plot(level['n'][~mask], level['excite'][~mask], lw=0, color=colors[phase], marker=marker[phase], markersize=ms)
                n_max = max(n_max, np.max(level['n']))
                if phase not in seen_key:
                    seen_key.append(phase)

    for phase in seen_key:
        ax.plot([], [], lw=lw, color=colors[phase], marker=marker[phase], markersize=ms, label=f'phase ${phase}$')
    latex_dict = {
        'K': r'K',
        'U': r'U',
        'g': r'g',
        'ed': fr'\varepsilon_{{d}}',
        'Gamma': fr'\Gamma',
        'eta': fr'\eta'
    } 
    if max(log_couplings(f'{path}/ander.log')) != 0:
        x0 = 0.75
        y0 = 0.8
        ax1 = ax.inset_axes([x0, y0, 1-x0, 1-y0])
        ms = 1 #markersize
        colors = {1:'r', 2:'g'}
        marker = '.'
        t_star, g_star = extract_t_star(ander_log)
        for phase in [1,2]:
            T = t_star[phase]
            G = g_star[phase]
            ax1.plot(np.log10(G), np.log10(np.abs(T)), lw=0.1, marker=marker, markersize=ms, color = colors[phase])  
        ax1.set_ylabel(r'$\log T^*$')
        latex_var = latex_dict[tuning_var_name]
        ax1.set_xlabel('$\log|D \mathrm{' + f'{latex_var}' +'}|$')      
    n1 = 0 #int(np.min(A[:,0]))
    n2 = n_max
    x_ticks = range(n1,n2+4,2)
    ax.set_xticks(x_ticks)
    ax.set_xlim(n1, n2+2)
    ax.legend(loc='upper left', fontsize='x-small')
    fig.tight_layout()
    fig.savefig(outimage, dpi=300)
    return 




def iexcdr_deocder(iexcdr):
    '''Decodes the iexcdr parameter in the ander.in file
    args: iexcdr(int)-->iexcdr parameter in the ander.in file
    returns: level(str)--> type of level being tracked by the driver'''

#     *     + If iexcdr = 0, E_e is the energy of the lowest excited state
# *       that has the same quantum numbers as the ground state and
# *       can therefore be intepreted as a bosonic excitation
# *     + If 1 <= iexcdr <= 100, E_e is the energy of the iexcdr'th
# *       f-channel fermionic excitation
# *     + If -100 <= iexcdr <= -1, E_e is the energy of the |iexcdr|'th
# *       excited state that has the quantum numbers to be a hole-like
# *       f-channel fermionic excitation
# *     + If iexcdr > 100, E_e is the energy of the (iexcdr-100)'th
# *       excited state that has the quantum numbers to be any f-channel
# *       fermionic excitation
# *     + If iexcdr < -100, E_e is the energy of the (|iexcdr|-100)'th
# *       excited state that has the quantum numbers to be any f-channel
# *       fermionic excitation, multiplied by -1 if that state has a
# *       smaller |Jfz| (or Jf) quantum number than the ground state.
    if iexcdr == 0:
        level = 'first bosonic excitation'
    elif 1<=iexcdr  and iexcdr <= 100:
        level = f'{iexcdr}th fermionic excitation'
    elif -100 <= iexcdr and iexcdr <= -1:
        level = f'{abs(iexcdr)}th hole-like fermionic excitation'
    elif iexcdr > 100:
        # evel = f'{iexcdr-100}th fermionic excitation'
        level = f'iexcdr={iexcdr}'
    elif iexcdr < -100:
        level = f'{abs(iexcdr)-100}th signed fermionic excitation'
    return level
