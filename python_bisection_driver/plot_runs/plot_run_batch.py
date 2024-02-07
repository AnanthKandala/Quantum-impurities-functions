import re
from natsort import natsort_keygen
import os 
from qim_functions import create
from python_bisection_driver import plot_driver_runs
import json
import time

if __name__ == '__main__':
    pwd = os.getcwd()
    run_direc = os.path.dirname(pwd)
    
    #check if all the runs are complete:
    natsort_key = natsort_keygen()
    directories = [name for name in os.listdir(run_direc) if '=' in name]
    directories.sort(key=natsort_key)
    status = True
    for direc in directories:
        if not os.path.isfile(f'{run_direc}/{direc}/script_output'): #no script_output file
            status = False
            print(f'Some calculations are incomplete')
            break
        else:
            if not 'Run complete!' in open(f'{run_direc}/{direc}/script_output').read():
                status = False
                print(f'Some calculations are incomplete')
                break
    if status: #all runs are complete
        print(f'All calculations are complete')
        with open(f'inputs.json') as f:
            function_inputs, params = json.load(f)
        nb = function_inputs['nb']; s = function_inputs['s']
        run_string = re.search(r'run\d+', run_direc).group()
        direc0 = os.path.dirname(run_direc)
        nrg_plot_direc = f'{direc0}/NRG_plots/{run_string}'
        create(nrg_plot_direc)
        os.system(f'rm -rf {nrg_plot_direc}/*')
        title_misc = f'$n_b={nb}$, {run_string}'
        start = time.time()
        count = 0
        while count < 10:
            try:
                plot_driver_runs(run_direc, nrg_plot_direc, s, title_misc, nb)
                break
            except Exception as e:
                if 'SyntaxError: not a PNG file' in str(e):
                    count += 1
                    print(e)
                    print(f'Plotting failed. Trying again. Attempt {count}')
                else:
                    raise e
        end = time.time()
        print(f'Plotting took {end-start} seconds')
        


    
    # #obtain the run_index from run_direc
    # run_string = re.search(r'run\d+', run_direc).group()
    
    # direc0 = os.path.dirname(run_direc)

    # nrg_plot_direc = f'{direc0}/NRG_plots/{run_string}'
    # create(nrg_plot_direc)
    # os.system(f'rm -rf {nrg_plot_direc}/*')


