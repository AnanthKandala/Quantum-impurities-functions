import os
from qim_functions import pdiff
import pandas as pd
import math 
from .single_run import single_run
from .calculate_phase import calculate_phase

def phase_boundary(tuning_var_name, tuning_var_limits):
    tuning_var_min = tuning_var_limits[0]
    tuning_var_max = tuning_var_limits[1]
    if tuning_var_name in ['ed', 'g']:
        boundary = {'delocalized': tuning_var_min, 'localized': tuning_var_max}
    elif tuning_var_name in ['Gamma']:
        boundary = {'delocalized': tuning_var_max, 'localized': tuning_var_min}
    return boundary

def format_float(val):
    return f'{val:.14f}'


def find_phase(run_direc, run_count, in_params:dict, nb:int, s:float, phase_tol, ander_data) -> str:
    #perform a single run:
    single_run(run_direc, run_count, nb, s, in_params, ander_data)
    phase = calculate_phase(s, f'{run_direc}/ander.out', phase_tol)
    return phase

# def find_run(var_count, fixed_var_name, tuning_var_name, tuning_var_limits, s, nb, tol, params):
def find_run(inputs):
    tuning_var_name, tuning_var_limits, s, nb, coupling_tol, phase_tol, params, ander_data = inputs
    run_count = 0
    pwd = os.getcwd()
    run_direc = pwd #location of the run directory
    run_results = {'run_index': [], 'tuning_var_value': [], 'phase': [], 'diff': [], 'min_var': [], 'max_var': []}
    boundary = phase_boundary(tuning_var_name, tuning_var_limits)
    os.system('touch ander.log')
    phase_tol = 10**-0.8        
    while abs(pdiff(boundary['delocalized'], boundary['localized'])) > coupling_tol:
        if run_count > 8 and len(run_results['phase']) < 2:
            os.system('touch convg_failed')
            break
        params[tuning_var_name] = 0.5*(boundary['delocalized']+boundary['localized'])
        phase = find_phase(run_direc, run_count, params, nb, s, phase_tol, ander_data)
        boundary[phase] = params[tuning_var_name]
        run_results['tuning_var_value'].append(params[tuning_var_name])
        run_results['phase'].append(phase)
        min_var = min(boundary.values())
        max_var = max(boundary.values())
        diff = round(math.log10(abs(pdiff(min_var, max_var))), 4)
        run_results['diff'].append(diff)
        run_results['min_var'].append(min_var)
        run_results['max_var'].append(max_var)
        run_results['run_index'].append(run_count)
        df = pd.DataFrame(run_results)
        columns_to_format = ['tuning_var_value', 'min_var', 'max_var']
        df[columns_to_format] = df[columns_to_format].apply(lambda x: x.map(format_float))

        with open('ander.log', 'w') as file:
            file.write(df.to_string(index=False))
        run_count += 1
    os.system(f'mv {run_direc}/ander.out {run_direc}/ander.out{run_count-1}')
    if len(run_results['phase']) > 2:
        print('Run complete!')
    else:
        print('Run failed to converge!')
    return
    