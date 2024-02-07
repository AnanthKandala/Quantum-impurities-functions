from .step1_helpers import create_man_dir, write_slurm_script, write_standard_in, launch_slurm_script
from qim_functions import parallel
import os
from functools import partial

def man_run_setup(pwd, Var_values_1, Var_values_2, nb, s):
    var_1_name = 'g'
    var_2_name = 'eta'
    os.system(f'rm -rf {pwd}')
    run_time = '04:30:00'
    U = 0.5
    Gamma = 0
    Delta = 0
    K = 100
    params = {  'U': U,
                'Gamma': Gamma,
                'Delta': Delta,
                'K': K,
                'N_max': 20
                }
    values_list = [(var_count_1, var_1, var_count_2,  var_2, var_1_name, var_2_name, pwd, nb, s, params, run_time) for var_count_1, var_1 in enumerate(Var_values_1) for var_count_2, var_2 in enumerate(Var_values_2)]
    parallel(man_run_step, values_list)
    count = len(values_list)
    print(f'count = {count}')   
    print(f"Submitted {count} SLURM jobs.")
    return 


def man_run_step(var_count_1, var_1, var_count_2,  var_2, var_1_name, var_2_name, pwd, nb, s, params, run_time):
        direc = f'{pwd}/{var_1_name}={var_count_1}/{var_2_name}={var_count_2}'
        title = f'man/{var_count_1}_{var_count_2}'
        create_man_dir(direc,nb,s)
        write_slurm_script(title,direc, run_time)
        eta = var_2
        ed = 0.5*(eta-1)*params['U']
        g = var_1
        
        params['ed'] = ed #params for the ander.in file
        params['g'] = g
        write_standard_in(f'{direc}/ander.in', **params)
        job_output = launch_slurm_script(direc)
        print(job_output.strip())
        return