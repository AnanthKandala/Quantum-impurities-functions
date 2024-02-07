import numpy as np
import pandas as pd
from qim_functions import aextr, pdiff, ander_in, eff_ander_in, worker
from plot_functions import cont_color
from run_functions import run_check_func
from functools import partial
import multiprocessing
import matplotlib.pyplot as plt
from matplotlib import rc,rcParams
import pickle as pkl
import os

rc('text', usetex=True)
rc('font', weight='bold')
custom_preamble = {
    "text.latex.preamble":
        r"\usepackage{amsmath,amssymb}" # for the align, center,... environment
        ,
    }


def get_optmized_derivatives(ander_out:str, par:str, column_header=None):
    '''Calculates the it iteration at which most levels become flat and returns the ediff values for that iteration.
    args:
        ander_out: ander.out file
        par: parity of the levels to be considered ['even', 'odd', 'all']
        column_header: column header to identify the run
    returns:
        ediff_frame: dataframe with the optimized ediff values for each level'''
    levels = aextr(ander_out, 3.0, par).query('sf == 0 and jf == 0')
    unique_qnums = levels.drop_duplicates(subset=['sf', 'jf', 'index'])[['sf', 'jf', 'index']]
    ediffs = {'n': levels['n'].unique()[:-1]}
    for (sf, jf, index) in unique_qnums.iloc:
        level = levels.query(f'energy<3.0 and sf == {sf} and jf == {jf} and index == {index}')
        energy = level['energy'].astype(float)
        if len(energy) > 3:
            if not np.all(energy == 0): #excluding the ground state energy
                ediff = np.abs(pdiff(energy[1:], energy[:-1]))
                if len(ediff) == len(ediffs['n']):
                    ediffs[(sf, jf, index)] = ediff
    ediff_frame =  pd.DataFrame(ediffs)
    minima_locations = ediff_frame.idxmin().to_numpy()
    min_rows, counts = np.unique(ediff_frame.idxmin().to_numpy(), return_counts= True)
    selected_row = min_rows[np.argmax(counts)]
    iteration = ediff_frame.iloc[selected_row].to_numpy()[0]
    #extremal values: 
    selected_ediffs = ediff_frame.iloc[[selected_row]].T[1:]
    return selected_ediffs, iteration


class ediff_plotter:
    def __init__(self):
        self.fig, self.ax = plt.subplots(dpi=300)
        self.ax.set_xlabel('$\eta$')
        self.ax.set_ylabel('$\log(Ediff)$')
        self.ax.set_ylim(-5, 1)
    
    def savefig(self, file_name):
        self.fig.savefig(file_name)


def fscore(path_blue:str, fixed_var_name:str, tuning_var_name:str, fixed_var_values, par:str, outimage:str, title_misc:str, return_iterations=False): 
    '''Calculated the optimized ediff values for all the directories in path_blue and finds the best eta value.
    args:
        path_blue [str]: location of the run directories
        fixed_var_name [str]: name of the fixed variable
        tuning_var_name [str]: name of the tuning variable
        fixed_var_values [list/ np.array]: list of the fixed variable values
        par [str]: parity of the levels to be considered ['even', 'odd', 'all']
        outimage [str]: name of the output image for the ediff plot
        title_misc [str]: additional string to be added to the title of the plot
    returns:
        index: the value of the index closest to the tricritical point
    '''

    #obtain the names of the tuning variables:
    directories = [f'{path_blue}/{fixed_var_name}={fixed_var_value}' for fixed_var_value in fixed_var_values]

    func = partial(get_optmized_derivatives, par=par)
    results = []
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        for result in pool.imap(worker, [(f'{direc}/last_runs/max.out', func) for direc in directories]):
            results.append(result)

    selected_ediffs = pd.concat([r[0] for r in results], axis=1) #all the ediffs.
    flat_iterations = [r[1] for r in results] #iteration for each run where the fscore was obtained
    selected_ediffs = selected_ediffs.dropna(axis=0) #remove rows with nan values
    plotter = ediff_plotter()
    ms = 2
    eta_values = [float(eff_ander_in(f'{direc}/last_runs', tuning_var_name)['eta']) for direc in directories]
    K = ander_in(f'{directories[0]}/last_runs/ander.in', 'find_driver')['K']
    for row in selected_ediffs.iterrows():
        # allowed_locs = np.where(~np.isnan(row[1].to_numpy()))[0]
        # allowed_eta = [eta_values[i] for i in allowed_locs]
        # allowed_ediff = [row[1].to_numpy()[i] for i in allowed_locs]
        # x = [fixed_var_values]
        plotter.ax.plot(fixed_var_values, np.log10(row[1].to_numpy(float)), 'k', lw=0.2, alpha=0.1, marker='.', markersize=ms)
        # plotter.ax.plot(allowed_eta, np.log10(allowed_ediff), 'k', lw=0.2, alpha=0.1, marker='.', markersize=ms)
        
        # plotter.ax.plot([eta_values[ed]]*len(special_values), np.log10(special_values), 'b', lw=0, alpha=0.1, marker='.', markersize=ms)
        # plotter.ax.plot([eta_values[ed]]*len(non_special_values), np.log10(non_special_values), 'k', lw=0, alpha=0.2, marker='.', markersize=ms)
    ediff_avg = selected_ediffs.mean(axis=0).to_numpy() #calculate the average ediff
    l = 0.2
    plotter.ax.plot(fixed_var_values, np.log10(ediff_avg), 'r', lw=l, marker='.', markersize=ms)
    best_run_index = np.argmin(ediff_avg)
    index = fixed_var_values[best_run_index]
    delta = np.array([eff_ander_in(f'{directories[i]}/last_runs', tuning_var_name)['ed'] for i in [best_run_index-1, best_run_index+1]]).astype(float)
    delta = np.abs(delta[1] - delta[0])
    best_ed = eff_ander_in(f'{directories[best_run_index]}/last_runs', tuning_var_name)['ed']
    plotter.ax.axvline(fixed_var_values[best_run_index], color='r', lw=l)
    plotter.ax.set_title(fr'\noindent {title_misc}, [${index}$] best_eta=${eta_values[best_run_index]}$[${best_ed}$], \newline $\delta \epsilon_d = {delta:.1e}$, iteration = ${int(selected_ediffs.iloc[0, best_run_index])}$, $K={K}$')    
    if len(outimage):
        plotter.savefig(outimage) 
    if return_iterations:
        return best_run_index, ediff_avg[best_run_index], flat_iterations
    else:
        return best_run_index, ediff_avg[best_run_index]
    

def plot_combined_fscore(path_blue:str, out_file:str):
    '''Plots the combined fscore for all the runs in the path
    args:
        path_blue: path to the blue runs
        title: title of the plot
        out_file: name of the output file
    returns:
        None'''
    assert os.path.isdir(path_blue), f'{path_blue} is not a valid directory'
    #obtain the list of all the directories with completed find runs
    frames = []
    run_paths = [path for path in os.listdir(path_blue) if os.path.isdir(os.path.join(path_blue, path)) and 'run' in path]
    for r in run_paths:
        run_path = f'{path_blue}/{r}'
        completed_runs = run_check_func(run_path)
        completed_runs['index'] = [f'{r}/{i}' for i in completed_runs['index']]
        frame = pd.DataFrame(completed_runs)
        frames.append(frame)
    combined_frame = pd.concat(frames, axis=0).sort_values(by=frames[0].columns[1], ascending=False).reset_index(drop=True) #has the locations and fixed/tuning var values for all the successful runs
    ander_outs = [f'{path_blue}/{i}/last_runs/max.out' for i in combined_frame['index']]

    #obtain the fscore for each of the runs
    par = 'all'
    inputs = [(f'{path_blue}/{row["index"]}/last_runs/max.out', par, row["index"]) for row in combined_frame.iloc]
    results = []
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        for result in pool.imap(worker, [(arg, get_optmized_derivatives) for arg in inputs]):
            results.append(result)
    all_ediffs = pd.concat([r[0] for r in results], axis=1).dropna(axis=0, how='any') #has the fscores for all the low-lying levels for all the successful runs
    flat_iterations = [r[1] for r in results]

    # plot_all_runs(path_blue, NRG_plot_direc, par, s, title_misc, extra_iterations)
    #plot all the fscores and average fscores. Identify the best runs
    fig, ax = plt.subplots(dpi=300)
    #generate 10 unique colors
    Colors = [cont_color(n,10, cmap=plt.cm.tab10) for n in range(10)]
    colors = [Colors[int(path.split('/')[0][-1])-1] for path in combined_frame['index']]
    lw = 0.1; s=2
    #compute column wise mean
    mean = all_ediffs.mean(axis=0).to_numpy(float)
    k_ideal = np.argmin(mean)
    best_run_location = combined_frame.iloc[k_ideal]['index']
    eta_values = combined_frame['eta'].to_numpy(float)
    x = range(len(all_ediffs.iloc[0]))
    # x = np.log10(eta_values - eta_values[k_ideal])
    ax.plot(x, np.log10(mean), lw=1, color='k', label='mean')

    ax.axvline(x[k_ideal], color='k', ls='--', lw=0.5, label='best')
    for path in np.unique(run_paths):
        k = int(path.split('n')[1][0])-1
        ax.scatter([],[], s=s, color=Colors[k], label=f'run {k+1}')
    for k, row in enumerate(all_ediffs.iloc):
        ax.plot(x, np.log10(np.array(row.values, dtype=float)), lw=lw, color='k', alpha=0.4)
        ax.scatter(x, np.log10(np.array(row.values, dtype=float)), s=s, color=colors, alpha=0.8)

    inputs_path = f'{path_blue}/inputs.pkl'
    with open(inputs_path, 'rb') as f:
        inputs = pkl.load(f)

    misc_path = f'{path_blue}/misc_dict.pkl'
    with open(misc_path, 'rb') as f:
        misc = pkl.load(f)

    title = fr"\noindent$s={misc['s']}$, $n_b = {misc['nb']}$, $U={inputs['U']}$, $g={inputs['g']}$\newline"
    title = fr'{title} best run: {best_run_location}'
    with open(f'{path_blue}/.best_run', 'w') as f:
        f.write(best_run_location)
    ax.set_title(title)
    ax.set_ylabel('fscore')
    ax.set_xlabel('')
    ax.set_ylim(-5, 1)
    ax.legend(loc=0, fontsize='small')
    fig.savefig(out_file)
    return flat_iterations