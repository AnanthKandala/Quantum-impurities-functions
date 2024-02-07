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
from qim_functions import extract_t_star


def plot_t_star(path:str, tuning_var_name:str):
    '''
    generates a plot of all the converged runs in the directory path
    args: path: str --> location of all the runs, fixed_var_name: str --> name of the fixed variable, 
             tuning_var_name: str --> name of the tuning variable
    returns: fig --> matplotlib figure object
    '''
    ms = 1 #markersize
    fig, ax = plt.subplots(dpi=500)
    Color = {1:'r', 2:'g'}
    for i in [1,2]:
        ax.plot([], [], color=Color[i], label=f'phase ${i}$')
    marker = '.'
    converged_runs = pd.read_csv(fr'{path}/completed_couplings.txt', sep=r'\s+')
    in_paths = [f'{path}/{run_path}' for run_path in converged_runs['index']]   
    for ll,run_path in enumerate(in_paths):
        #reading the log file and analyzing for convergence
        ander_log = f"{run_path}/ander.log"
        t_star, g_star = extract_t_star(ander_log)
        for phase in [1,2]:
            T = t_star[phase]
            G = g_star[phase]
            ax.plot(np.log10(G), np.log10(np.abs(T)), lw=0.1, marker=marker, markersize=ms, color = Color[phase])        
    ax.set_ylabel(r'$\log T^*$')
    latex_dict = {
        'K': r'K',
        'U': r'U',
        'g': r'g',
        'ed': fr'\varepsilon_{{d}}',
        'Gamma': fr'\Gamma',
        'eta': fr'\eta'
    } 
    latex_var = latex_dict[tuning_var_name]
    ax.set_xlabel(fr'$\log| 1 - {latex_var}/{latex_var} c|$')
    ax.legend(loc=0, fontsize='small')
    plt.tight_layout()
    plt.close(fig)
    return fig