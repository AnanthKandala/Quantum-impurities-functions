import numpy as np
import os
import pickle as pkl
from functools import partial
from run_functions import run_check_func
from plot_functions import plot_all_runs
from f_based_Tp_automation import run_complete_check, fscore, start_new_batch, plot_combined_fscore
from qim_functions import eff_ander_in, extract_level

def status_statement(run_index:int, completed_runs:str, fixed_var:float, fixed_var_diff:float, tuning_var:float, best_run_path=None):
    '''Takes the inputs and formats them so that they can be appended to the automation_status.txt file
        args:
            run_index: index of the run
            completed_runs: no. of successful runs/ total number of runs
            fixed_var: value of the fixed variable
            fixed_var_diff: size of the window for the Tp fixed point
            tuning_var: value of the tuning variable found by the find driver
        '''
                #  1           15/15               -2.295375     1.250000e-04  0.00176984281806921   8.108908e-02
    string = f'{run_index}           {completed_runs}               {str(fixed_var).zfill(8)}   {fixed_var_diff:3e}  {str(tuning_var).zfill(17)}   {fscore:3e}  {best_run_path}\n'
    return string


if __name__ == '__main__':
    pwd = os.getcwd()
    run_direc = os.path.dirname(pwd)
    direc0 = os.path.dirname(run_direc)
    print(f'run_direc: {run_direc}')
    with open(f'{direc0}/misc_dict.pkl', 'rb') as file1: # obtain common values in the calculation:
        misc_dict = pkl.load(file1)
    #misc_dict contains values of nb, run_index, s, fixed_var_name, tuning_var_name, num_runs, ed_tol
    for key, value in misc_dict.items():
        globals()[key] = value

    #obtain the values of completed runs:
    status, completed_runs = run_complete_check(run_direc, fixed_var_name, tuning_var_name, num_runs)
    if status:
        if len(completed_runs) == 0: #No runs compelte
            # statement = status_statement(run_index, len(completed_runs), '---', '---', '---')
            statement = 'No runs complete'
            
        else: #All runs have completed
            fixed_var_values = np.array([eff_ander_in(f'{run_direc}/{fixed_var_name}={var}', tuning_var_name)[fixed_var_name] for var in completed_runs]).astype(np.float64)
            tuning_var_values = np.array([eff_ander_in(f'{run_direc}/{fixed_var_name}={var}', tuning_var_name)[tuning_var_name] for var in completed_runs]).astype(np.float64)
            
        # ----------Obtain the ediff closest to Tp ---------------------------------
            outimage = f'{direc0}/fscore_run{run_index}.png'; par = 'all'; title_misc = f'run_index=${run_index}$'
            return_iterations = True
            ind, fscore, extra_iterations = fscore(run_direc, fixed_var_name, tuning_var_name, completed_runs, par, outimage, title_misc, return_iterations)
            count = 0
            extra_iterations = [(n,) for n in extra_iterations]
            plot_all_runs(run_direc, f'{direc0}/NRG_plots/run{run_index}', 'all', s, f'$n_b={nb}$,run${run_index}$', extra_iterations)

            while count < 10:
                try:
                    break
                except Exception as e:
                    if 'SyntaxError: not a PNG file' in str(e):
                        count += 1
                        print(e)
                        print(f'Plotting failed. Trying again. Attempt {count}')
                    else:
                        raise e
            ed_diff = np.abs(fixed_var_values[ind+1] - fixed_var_values[ind-0])
            ed = fixed_var_values[ind]; Gamma = tuning_var_values[ind]
            statement = status_statement(run_index, len(completed_runs), fixed_var_values[ind], ed_diff, tuning_var_values[ind], f'{run_direc}/{fixed_var_name}={ind}')
            #------------------------If ed has not converged, start a new batch of calculations------------------------
            if ed_diff > ed_tol: #the runs need to continue
                # obtain the common inputs in all the calculations. Contains values of U, g, K, drepos, dreneg
                with open(f'{direc0}/inputs.pkl', 'rb') as file1:
                    inputs = pkl.load(file1)

                run_ids = np.unique([completed_runs[ind-1], completed_runs[ind+1]])
                #obtain the bounds on the fixed and tuning variable
                fixed_var_bounds = [fixed_var_values[ind-1], fixed_var_values[ind+1]]; tuning_var_bounds = [tuning_var_values[ind-1], tuning_var_values[ind+1]]
                
                #obtain revised thresholds
                # if abs(inputs['drepos'] - inputs['dreneg']) > 0.01:
                #     e_flats = []
                #     for i in [ind-1, ind, ind+1]:
                #         level = extract_level(f'{run_direc}/ed={i}/last_runs/max.out', [0,0,1], 'all')['energy'].to_numpy(float)
                #         e_flat = levels[np.argmin(np.abs(np.diff(levels)))]
                #         e_flats.append(e_flat)
                #     e_flats_diff = 0.5*(np.max(e_flats)- np.min(e_flats))
                #     p = 0.5
                #     inputs['dreneg'] = np.min(e_flats)-p*(e_flats_diff); inputs['drepos'] = np.max(e_flats)+p*(e_flats_diff)

                #-----------------------------------------start a new batch of calculations----------------------------------------- 
                misc_dict['run_index'] += 1
                with open(f'{direc0}/misc_dict.pkl', 'wb') as f:
                    pkl.dump(misc_dict, f)
                new_run_direc = f'{direc0}/run{misc_dict["run_index"]}'
                start_new_batch(new_run_direc, misc_dict, inputs, fixed_var_bounds, tuning_var_bounds)
            else: #runs have converged. Plot the final fscore and the final run
                plot_combined_fscore(direc0, f'{direc0}/final_fscore.png') #plot the final fscore for the runs
                statement = 'All runs are complete'
            with open(f'{direc0}/automation_status.txt', 'a') as f:
                f.write(statement)
    else:
        print('Some runs are not complete.')