import numpy as np
import pandas as pd
import math
import os
from run_functions import obtain_variable_values
from qim_functions import ander_in


def run_check(pwd:str, save_path:str) -> None:
    fixed_var_name = 'g'
    _, var_values = obtain_variable_values(pwd)
    tuning_var_name = 'ed'
    # print(fixed_var_name, tuning_var_name)
    STATUS=[]
    E=[]
    completed_runs = {'index':[], f'{fixed_var_name}':[], f'{tuning_var_name}_c': []}
    for var_value in var_values:
        path = os.path.join(pwd, f"{fixed_var_name}={var_value}")
        ander_log = os.path.join(path, f"ander.log")
        if os.path.exists(path):
            with open(ander_log, "r") as f:
                all_lines = f.readlines()
            Index = []
            G = []
            Phase = []
            L = len(all_lines)
            if L==0:
                status_string = 'empty log file!'
            else:
                with open(f"{path}/script_output", 'r') as f:
                        script_string = f.read()
                if 'TIME LIMIT' in script_string:
                    SLURM_status = 'SLURM:stopped (time limit reached!),'
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
                        critical_coupling = 0.5*(min_coupling + max_coupling)
                        N_star = all_lines[last_index-1].split()[3]
                        T_star = round(math.log10(abs(float(all_lines[last_index-1].split()[2]))), 2)
                        diff = all_lines[last_index].split()[-1]
                        
                        fixed_var_value = ander_in(os.path.join(path,"ander.in"), 'find')[fixed_var_name]
                        completed_runs[f'{fixed_var_name}'].append(fixed_var_value)
                        completed_runs[f'{tuning_var_name}_c'].append(critical_coupling)
                        completed_runs['index'].append(var_value)
                        
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
                STATUS=np.append(STATUS,[status_string])
        else:
            status_string = 'no such directory!'    
            STATUS=np.append(STATUS,[status_string])

    if tuning_var_name=='ed':
        completed_runs['eta_c'] = 1 + (2*np.array(completed_runs['ed_c']).astype(float)/float(ander_in(os.path.join(path,"ander.in"), 'find')['U']))
    completed_runs_df = pd.DataFrame(completed_runs)
    completed_runs_df.to_csv(save_path, sep='\t',index=False, header=True)
    print(f'created {save_path}')
    return 


    # if len(completed_runs)>0:
    #    #, columns=['index', fixed_var_name, f'{tuning_var_name}_c'])
    #     if tuning_var_name=='ed':
    #         completed_runs['eta_c'] = 1 + (2*np.array(completed_runs_df['ed_c'])/ander_in(os.path.join(path,"ander.in"), 'find')['U'])
    #     completed_runs_df = pd.DataFrame(completed_runs)
    #     completed_runs_df.to_csv('var_completed.txt', sep='\t',index=False, header=True)
    
    # if len(STATUS): 
    #     status_df = pd.DataFrame({'variable_value': var_values, 'status': STATUS})
    #     status_df.to_csv('STATUS.txt', sep='\t',index=False, header=True, quoting=csv.QUOTE_NONE)
    # else:
    #     print('status is empty!')