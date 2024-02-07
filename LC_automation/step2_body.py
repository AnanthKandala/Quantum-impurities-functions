import numpy as np
import os 
from .step2_helpers import stable_fixed_point, plot_phase, write_edc_SLURM, write_edc_in, create_edc_dir, launch_slurm_script
from qim_functions import ander_in, create, parallel
from run_functions import obtain_variable_values

def obtain_man_boundary(pwd, plot_path, s, nb):
    '''obtains the phase boundary from the manual runs and plots the phase diagram at plot_path'''
    var_1_name = 'g'
    var_2_name = 'eta'

    _, Var_values_1  = obtain_variable_values(pwd)
    _, Var_values_2 = obtain_variable_values(f'{pwd}/{var_1_name}={Var_values_1[0]}')
    phase = np.empty((len(Var_values_1), len(Var_values_2)))
    G = np.empty(len(Var_values_1))
    Ed = np.empty(len(Var_values_2))
    x = np.empty(len(Var_values_1)*len(Var_values_2))
    y = np.empty(len(Var_values_1)*len(Var_values_2))
    z = np.empty(len(Var_values_1)*len(Var_values_2))
    count = 0
    for i1, var1 in enumerate(range(len(Var_values_1))):
        for i2, var2 in enumerate(range(len(Var_values_2))):
            direc = f'{pwd}/{var_1_name}={var1}/{var_2_name}={var2}'
            ander_out = f'{direc}/ander.out'
            inputs = ander_in(f'{direc}/ander.in', 'standard')
            ed = inputs['ed']
            g = inputs['g']
            phase[i1, i2] = stable_fixed_point(ander_out, s)
            x[count] = float(g)
            y[count] = float(inputs['eta'])
            z[count] = phase[i1, i2]
            G[i1] = float(g)
            Ed[i2] = float(ed)
            count += 1

    #obtain the boundary:
    G_boundary = []
    Ed_min = []
    Ed_max = []
    for i1, g in enumerate(G): #looping over g
        phases = [i in phase[i1,:] for i in [0,1]]
        if all(phases): #if both phases are present
            ed_min = np.max(Ed[np.where(phase[i1,:]==0)])
            ed_max = np.min(Ed[np.where(phase[i1,:]==1)])
            Ed_min.append(ed_min)
            Ed_max.append(ed_max)
            G_boundary.append(g)
    K = int(inputs['K'])
    U = float(inputs['U'])
    plot_title = fr'\noindent $s={s}$, $n_b={nb}, K={K}$'
    eta_boundary = [1+ (Ed_max[i] + Ed_min[i])/U for i in range(len(Ed_max))]
    # plot_phase(plot_path, x, y,z, plot_title,G_boundary, eta_boundary)
    return G_boundary, Ed_min, Ed_max




def edc_run_setup(pwd, G_boundary, Ed_min, Ed_max, nb, s):
    Var_values = G_boundary
    Var_min = Ed_min
    Var_max = Ed_max
    os.system(f'rm -rf {pwd}/g*')
    input_args = [(pwd, var_count, var, Var_min, Var_max, s, nb) for var_count, var in enumerate(Var_values)]
    parallel(step, input_args)
    count = len(Var_values)
    print(f'count = {count}')   
    print(f"Submitted {count} SLURM jobs.")
    return

def step(pwd, var_count, var, Var_min, Var_max, s, nb):
        var_name = 'g'
        Gamma = 0
        Delta = 0
        U = 0.5
        K = 200
        
        create(pwd)
        run_time = '10:30:00' 
        title = f'{s},nb={nb}/{var_count}'
        direc = f'{pwd}/{var_name}={var_count}'
        create_edc_dir(direc,nb,s)
        tune_var_max = Var_max[var_count]
        tune_var_min = Var_min[var_count]
        assert tune_var_min < tune_var_max
        e_d = 0.5*(tune_var_max + tune_var_min)#round((eta-1)*0.5*U, 5)
        g = var
        #params for the ander.in file
        params = {
            'e_d': e_d,
            'U': U,
            'Gamma': Gamma,
            'Delta': Delta,
            'g': g,
            'K': K,
            'var_min': tune_var_min, 
            'var_max': tune_var_max
            }
        write_edc_SLURM(title, direc, run_time)
        write_edc_in(f'{direc}/ander.in', **params)
        job_output = launch_slurm_script(direc)
        print(job_output.strip())
        return