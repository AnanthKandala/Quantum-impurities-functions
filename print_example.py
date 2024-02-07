import numpy as np
import os 
from run_functions import input_check, create_run_dir, write_slurm_script, launch_slurm_script, wrun, sigint_handler
from functools import partial
from qim_functions import parallel
import signal


#prints ander.in:
def write_in(f,ed,U,Gamma, Delta,g, K, var_min, var_max) -> None:
    with open(f, 'w') as file1:
         file1.write('{0} {1} 1d-13    100'.format(var_min, var_max)+'\n')
         file1.write(' 0      0   0.01 0.36     -3'+'\n')
         file1.write(f'{ed} {U} {Gamma}  0.0    0.0    0.0'+'\n')
         file1.write(f'0.0    0.0    {g}    0.0    0.0    1.0      0'+'\n')
         file1.write('0.0    0.0    0.0    0.0    0.0    0.0    0.0'+'\n')
         file1.write(f'{Delta}    0.0    0.0    0.0                          1'+'\n')
         file1.write('9.0    0.0    0.0          1d-6         1d-20'+'\n')
         file1.write(f'0     50      0   {K}      0      1      0     0'+'\n')
         file1.write('5    0.6'+'\n')
    return



def init_run_dir(path:str,nb:int, s:float=None, r:float=None) -> None:
    '''creates a directory with ander, ander.band/bath and ander.data files '''
    ander_exec = r'find_Gammac_bfam.1000.1_-1:15_7June2023'
    ander_data = r'1_-1:7_flocal.data_2Aug2023'
    files = {'ander': ander_exec, 'ander.data': ander_data}
    create_run_dir(path, files, s, r)
    return 

def step(var_count, fixed_var_value, fixed_var_name, nb, s, r, params):
    run_direc = os.path.join(os.getcwd(), f'{fixed_var_name}={var_count}') #location of the run directory
    os.system(f'rm -rf {run_direc}') #delete existing instance of the run directory
    title = f'phsym/{run_direc}' #title for the slurm script
    init_run_dir(run_direc, nb, s, r) #initialize the run directory
    write_slurm_script(title,run_direc, run_time) #write the slurm script
    params[fixed_var_name] = fixed_var_value #set the value of the fixed variable
    write_in(f'{run_direc}/ander.in', **params) #write the ander.in file
    launch_slurm_script(run_direc) #launch the slurm script
    print(f'{fixed_var_name} = {fixed_var_value} [{var_count}]') #print the progress
    return


if __name__ == '__main__':
    # Var_values, Var_max, Var_min = np.loadtxt('couplings.txt', unpack=True)
    nb = 7
    r = None
    s = 0.6

    #details of the fixed variable
    params = {}     #params for the ander.in file
    params['U'] = 0.5
    fixed_var_name = 'ed'
    ed_min = -2.86312625502244
    ed_max = -0.5*params['U']
    fixed_var_values = np.linspace(ed_min, ed_max, 100)

    #details of the tuning variable
    tuning_var_name = 'Gamma'
    params['var_min'] = 0.0001; params['var_max'] = 10.0
    params[tuning_var_name] = 0.5*(params['var_min'] + params['var_max'])
    print(f'submitting {len(fixed_var_values)} jobs')
    params['g'] = 5.0
    params['Delta'] = 0
    params['K'] = 100

    input_check(params, fixed_var_name) #checks if the inputs to the driver are properly set.

    run_time = '04:30:00' #time for the slurm script

    partial_step = partial(step, fixed_var_name=fixed_var_name, nb=nb, s=s, r=r, params=params)
    parallel(partial_step, list(enumerate(fixed_var_values)))
    print(f'submitted {len(fixed_var_values)} jobs')
    os.system('bash ~/wrun.csh')
    
