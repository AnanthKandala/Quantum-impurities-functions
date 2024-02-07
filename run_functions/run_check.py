import numpy as np
import pandas as pd
import math
import os
from qim_functions import eff_ander_in, obtain_names
import csv
import multiprocessing
from natsort import natsort_keygen

def run_check_func(pwd):
    # _, var_values = obtain_variable_values(pwd)
    natsort_key = natsort_keygen()
    directories = [f'{pwd}/{name}' for name in os.listdir(pwd) if '=' in name]
    directories.sort(key=natsort_key)
    names_dic = obtain_names(pwd)
    fixed_var_name = names_dic['fixed_var_name']; tuning_var_name = names_dic['tuning_var_name']
    print(f'fixed_var_name={fixed_var_name}, tuning_var_name={tuning_var_name}')
    input_args = [(direc, tuning_var_name) for direc in directories]
    with multiprocessing.Pool() as pool:
        results = pool.starmap(status, input_args)
    STATUS = [i[0] for i in results]

    completed_runs = {'index':[], f'{fixed_var_name}':[], f'{tuning_var_name}_c': []}
    for c in [c for c, i in enumerate(results) if i[1]]:
        path = os.path.join(pwd, directories[c])
        eff_inputs = eff_ander_in(path, tuning_var_name)
        U = float(eff_inputs['U'])
        fixed_var_value = eff_inputs[f'{fixed_var_name}']
        critical_coupling = eff_inputs[f'{tuning_var_name}']
        completed_runs[f'{fixed_var_name}'].append(fixed_var_value)
        completed_runs[f'{tuning_var_name}_c'].append(critical_coupling)
        completed_runs['index'].append(directories[c].split('/')[-1])


    if len(completed_runs['index'])>0:
        print(f'completed_runs={completed_runs}')
        if fixed_var_name=='ed':
            completed_runs['eta'] = 1 + (2*np.array(completed_runs['ed']).astype(float)/U)
        if tuning_var_name=='ed':
            completed_runs['eta_c'] = 1 + (2*np.array(completed_runs['ed_c']).astype(float)/U)
        completed_runs_df = pd.DataFrame(completed_runs)
        completed_runs_df.to_csv(f'{pwd}/completed_couplings.txt', sep='\t',index=False, header=True)
    if len(STATUS): 
        print_directories = [direc.split('/')[-1] for direc in directories]
        status_df = pd.DataFrame({'run_directories': print_directories, 'status': STATUS})
        status_df.to_csv(f'{pwd}/STATUS.txt', sep='\t',index=False, header=True, quoting=csv.QUOTE_NONE)
    else:
        print('status is empty!')
    return completed_runs



def status(path:str, tuning_var_name:str) -> (str, bool):
    ander_log = os.path.join(path, f"ander.log")
    try:
        if os.path.exists(path):
            with open(ander_log, "r") as f:
                all_lines = f.readlines()
            calc_status = False
            L = len(all_lines)
            if L==0:
                status_string = 'empty log file!'
            else:
                with open(f"{path}/script_output", 'r') as f:
                        script_string = f.read()
                if 'TIME LIMIT' in script_string:
                    SLURM_status = 'SLURM:stopped [time limit reached!],'
                elif 'CANCELLED' in script_string:
                    SLURM_status = 'SLURM:stopped [cancelled],'
                elif script_string.count('EDT')==1:
                    SLURM_status = 'SLURM:runing,'
                elif script_string.count('EDT')==2:
                    SLURM_status = 'end'
                else:
                    SLURM_status = 'unknown'
                
                all_codes = []
                for line_count, line in enumerate(all_lines):
                    if '>' in line:
                        code = line.split()[-1]
                        if code not in all_codes:
                            all_codes.append(code)
                
                line_ind = len(all_lines)-1
                while line_ind>0:
                    line = all_lines[line_ind]
                    end_line = '**'in line
                    non_stable_run = '>'in line
                    if not end_line and not non_stable_run:
                        min_coupling = float(line.split()[0])
                        max_coupling = float(line.split()[1])
                        last_index = line_ind
                        line_ind = -1
                    else:
                        line_ind += -1
                
                if '**' in all_lines[-1] and 'not' not in all_lines[-1]:
                    
                    if False not in [i in all_codes for i in ['1', '2']]:
                        log_status = 'converged,'
                        calc_status = True
                        critical_coupling = 0.5*(min_coupling + max_coupling)
                        N_star = all_lines[last_index-1].split()[3]
                        T_star = round(math.log10(abs(float(all_lines[last_index-1].split()[2]))), 2)
                        diff = all_lines[last_index].split()[-1]
                        status_string = f"{SLURM_status} {log_status} phs={all_codes}| diff={diff} T_*=({N_star}){T_star}| {tuning_var_name}={critical_coupling}"
                    else:
                        log_status = 'completed:only single phase found'
                        status_string = '{0} {1},  phases={2} |couplings={3}|'.format(SLURM_status, log_status, all_codes, [min_coupling, max_coupling])
                
                elif '**' in all_lines[-1] and 'not' in all_lines[-1]:
                    log_status = 'log file:not converged!'
                    if False not in [i in all_codes for i in ['1', '2']]:
                        status_string = '{0} {1},  phases={2} |couplings={3}|'.format(SLURM_status, log_status, all_codes, [min_coupling, max_coupling])
                    else: 
                        status_string = '{0} {1},  phases={2}'.format(SLURM_status, log_status, all_codes)
                elif '-4' in all_codes:
                    log_status = 'log file:ander.stopped!'
                    status_string = '{0} {1}, phases={2} |couplings={3}|'.format(SLURM_status, log_status, all_codes, [min_coupling, max_coupling])
                else:
                    log_status = ''#'log file:running,'
                    N_star = all_lines[last_index-1].split()[3]
                    T_star = round(math.log10(abs(float(all_lines[last_index-1].split()[2]))), 2)
                    diff = all_lines[last_index].split()[-1]
                    status_string = f"{SLURM_status} {log_status} phs={all_codes}| diff={diff} T_*=({N_star}){T_star}| {tuning_var_name} = [{min_coupling}, {max_coupling}]"
        else:
            status_string = 'no such directory!'  
            calc_status = False  
    except:
        status_string = 'error!'
        calc_status = False
    return status_string, calc_status