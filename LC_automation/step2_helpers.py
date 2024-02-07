import numpy as np
from qim_functions import aextr, pdiff, create, free_boson_energy
import os 
import subprocess

import matplotlib.pyplot as plt
from matplotlib import rc,rcParams
rc('text', usetex=True)
rc('font', weight='bold')
custom_preamble = {
    "text.latex.preamble":
        r"\usepackage{amsmath,amssymb}" # for the align, center,... environment
        ,
    }
plt.rcParams.update(custom_preamble)



def stable_fixed_point(ander_out, s):
    '''function that checks if the fixed point is a free-boson or localized
    args: ander_out (str): --> path to the input file, s (float): bath exponent
    returns: phase (int) --> phase=1 if free boson, phase=2 if localized
    ''' 
    e_b = free_boson_energy(s) #free bosonic energy
    spectrum = aextr(ander_out, 3.0, 'all')
    n_max = spectrum['n'].max()
    condition = (spectrum['n'] == n_max)
    last_iter = spectrum[condition]
    energies = last_iter['energy']
    #check if all the energies in the last iteration are free-bosonic:
    diff = [pdiff(e, i*e_b) for i, e in enumerate(energies)]
    max_diff = max(diff)
    if max_diff<0.5: #stable fixed point is made of only free bosonic energies
        phase = 0
    else: #If no free bosons, then the fixed point is localized
        phase = 1
    return phase



def plot_phase(plot_path, x, y,z, title, G_boundary, eta_boundary):
    fig, ax = plt.subplots()
    ax.set_xlabel('$g$')
    ax.set_ylabel('$\eta$')
    marker = {0:'.' , 1:'x'}
    color = {0:'r' , 1:'g'}
    Name = {0:'free boson' , 1:'Loc'}
    ms = 2
    ax.set_title(title)
    ax.axhline(-1, color='k', linestyle='--')
    for phase, name in Name.items():
        x_selected = x[np.where(z==phase)]
        y_selected = y[np.where(z==phase)]
        ax.plot(x_selected, y_selected, marker=marker[phase], color=color[phase], label=f'{name}', ms=ms, lw=0)
    ax.plot(G_boundary, eta_boundary, marker='.', color='k', ms=ms, lw=0.5)
    ax.legend(loc=0)
    plt.tight_layout()
    plt.savefig(f'{plot_path}/phase_diag.png', dpi=300)
    plt.close()
    return 
    


def write_edc_SLURM(title, direc, run_time):
    '''
    Writes a SLURM script to {var_name}={var_value}/SLURM.
    args: slurm_file-->string, title-->string, var_name-->string, var_value-->string, time-->string (format: 'hh:mm:ss')
    returns: None
    '''
    # pwd = str(os.getcwd())
    with open(f'{direc}/SLURM','w') as file2:
         file2.write('#!/bin/bash'+'\n')
         file2.write('#SBATCH --job-name={}   # Job name'.format(title)+'\n')
         file2.write('#SBATCH --mail-type=FAIL,END          # Mail events (NONE, BEGIN, END, FAIL, ALL) '+'\n')
         file2.write('#SBATCH --account=physics-dept'+'\n')
         file2.write('#SBATCH --qos=physics-dept'+'\n')
         file2.write('#SBATCH --ntasks=1                    # Run on a single CPU'+'\n')
         file2.write('#SBATCH --mem=1Gb                     # Job memory request'+'\n')
         file2.write(f'#SBATCH --time={run_time}               # Time limit hrs:min:sec'+'\n')
         file2.write('#SBATCH --output=script_output   # Standard output and error log'+'\n')
         file2.write('pwd; hostname; date'+'\n')
         file2.write('module load gcc/8.2.0'+'\n')
         file2.write('module load lapack/3.8.0'+'\n')
         string = f'{direc}/ander'
         file2.write(string+'\n')
         file2.write('date')
    return


def write_edc_in(f,e_d,U,Gamma, Delta,g, K, var_min, var_max):
    with open(f, 'w') as file1:
         file1.write('{0} {1} 1d-13    100'.format(var_min, var_max)+'\n')
         file1.write('0      -101  -2.0 -0.001    -3'+'\n')
         file1.write(f'{e_d} {U} {Gamma}  0.0    0.0    0.0'+'\n')
         file1.write(f'0.0    0.0    {g}    0.0    0.0    1.0      0'+'\n')
         file1.write('0.0    0.0    0.0    0.0    0.0    0.0    0.0'+'\n')
         file1.write(f'{Delta}    0.0    0.0    0.0                          1'+'\n')
         file1.write('9.0    0.0    0.0          1d-6         1d-20'+'\n')
         file1.write(f'0     50      0   {K}      0      1      0     0'+'\n')
         file1.write('5    0.6'+'\n')
    return


def launch_slurm_script(slurm_dir):
    # Use sbatch to submit the SLURM script and capture the output
    result = subprocess.run(['sbatch', 'SLURM'], check=True, stdout=subprocess.PIPE,  cwd=slurm_dir)
    output = result.stdout.decode('utf-8')
    return output






def create_edc_dir(path,nb,s):
    '''creates the basic skeleton of the directory for find edc runs '''
    create(path)
    #ander
    p1 = r'/home/an.kandala/proj/anderson/src/nrg/my_Keep/Hipergator/loginnodes/find_edc_bfam.1000:1_-1:15_flocal_3June2023'
    os.system(f'ln -s {p1} {path}/ander')
    #ander.data
    p2 = fr'/home/an.kandala/proj/anderson/bin/linux/Keep/login_nodes/LC_automation/1_-1:{nb}_withoutfermions.data'
    os.system(f'ln -s {p2} {path}/ander.data')
    #ander.bath
    p3 = fr'/home/an.kandala/proj/discretization/1imp/9/s={s}'
    os.system(f'ln -s {p3} {path}/ander.bath')
    return