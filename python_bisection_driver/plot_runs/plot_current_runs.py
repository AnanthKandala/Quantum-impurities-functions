import re
from natsort import natsort_keygen
import os 
from qim_functions import create
from python_bisection_driver import plot_temp_runs
import json
import time


if __name__ == '__main__':
    runs_directory = os.getcwd()
    direc0 = os.path.dirname(runs_directory)
    
    #check if all the runs are complete:
    natsort_key = natsort_keygen()
    directories = [name for name in os.listdir(runs_directory) if '=' in name]
    directories.sort(key=natsort_key)
    run_string = re.search(r'run\d+', runs_directory).group()
    nrg_plot_direc = f'{direc0}/temp_plots/{run_string}'
    create(nrg_plot_direc)
    os.system(f'rm -rf {nrg_plot_direc}/*')
    if len(directories) == 0:
        raise Exception('No runs found')
    else:
        with open(f'{directories[0]}/inputs.json') as f:
            function_inputs, params = json.load(f)
        nb = function_inputs['nb']; s = function_inputs['s']
        title_misc = f'$n_b={nb}$, {run_string}'
        start = time.time()
        plot_temp_runs(runs_directory, nrg_plot_direc, s, title_misc, nb)
        end = time.time()
        print(f'Plotting took {end-start} seconds')
        



