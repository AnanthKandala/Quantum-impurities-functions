import numpy as np
import os 
from qim_functions import create
# from run_functions import *
import subprocess

def write_slurm_script(title: str, directory: str, run_time: str) -> None:
    '''
    Writes a SLURM script to {directory}/SLURM.

    Args:
        title (str): Job name.
        directory (str): Directory to write the SLURM script to.
        run_time (str): Time limit in the format 'hh:mm:ss'.
    '''
    with open(f'{directory}/SLURM', 'w') as file:
        # SLURM script header
        file.write('#!/bin/bash\n')
        file.write(f'#SBATCH --job-name={title}   # Job name\n')
        file.write('#SBATCH --mail-type=FAIL,END          # Mail events (NONE, BEGIN, END, FAIL, ALL)\n')
        file.write('#SBATCH --account=physics-dept\n')
        file.write('#SBATCH --qos=physics-dept\n')
        file.write('#SBATCH --ntasks=1                    # Run on a single CPU\n')
        file.write('#SBATCH --mem=1Gb                     # Job memory request\n')
        file.write(f'#SBATCH --time={run_time}               # Time limit hrs:min:sec\n')
        file.write('#SBATCH --output=script_output   # Standard output and error log\n')
        file.write('pwd; hostname; date\n')
        # Load modules
        file.write('module load gcc/8.2.0\n')
        file.write('module load lapack/3.8.0\n')
        # Run command
        command = f'{directory}/ander'
        file.write(f'{command}\n')
        file.write('date')
    return



def write_standard_in(file: str, ed: float, U: float, Gamma: float, Delta: float, g: float, K: int, N_max:int) -> None:
    '''writes the ander.in file for a standard single run'''
    with open(file, 'w') as file1:
         file1.write(f'{ed} {U} {Gamma}  0.0    0.0    0.0'+'\n')
         file1.write(f'0.0    0.0    {g}    0.0    0.0    1.0      0'+'\n')
         file1.write('0.0    0.0    0.0    0.0    0.0    0.0    0.0'+'\n')
         file1.write(f'{Delta}    0.0    0.0    0.0                          1'+'\n')
         file1.write('9.0    0.0    0.0          1d-6         1d-20'+'\n')
         file1.write(f'0     {N_max}     0   {K}      0      1      0     0'+'\n')
         file1.write('5    0.6'+'\n')
    return




def launch_slurm_script(slurm_dir):
    # Use sbatch to submit the SLURM script and capture the output
    result = subprocess.run(['sbatch', 'SLURM'], check=True, stdout=subprocess.PIPE,  cwd=slurm_dir)
    output = result.stdout.decode('utf-8')
    return output






def create_man_dir(path,nb,s):
    '''creates the basic skeleton of the directory for manual runs '''
    create(path)
    #ander
    p1 = r'/home/an.kandala/proj/anderson/src/nrg/my_Keep/Hipergator/loginnodes/1.1000_-1:15_flocal_22July2023'
    os.system(f'ln -s {p1} {path}/ander')
    #ander.data
    p2 = fr'/home/an.kandala/proj/anderson/bin/linux/Keep/login_nodes/LC_automation/1_-1:{nb}_withoutfermions.data'
    os.system(f'ln -s {p2} {path}/ander.data')
    #ander.bath
    p3 = fr'/home/an.kandala/proj/discretization/1imp/9/s={s}'
    os.system(f'ln -s {p3} {path}/ander.bath')
    return