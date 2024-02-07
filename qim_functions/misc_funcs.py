import pandas as pd
import os
import multiprocessing
from collections import OrderedDict
from IPython.display import display_html
import numpy as np
import re
import json
import inspect


def create(path):
    os.makedirs(path, exist_ok=True)
    return

def worker(args):
    arg, func = args
    return func(*arg) if isinstance(arg, tuple) else func(arg)


def parallel(func, list_args:list, num_processes:int = multiprocessing.cpu_count(), return_arg=False, save_job_ids=False, save_direc=os.getcwd()):
    '''
    Runs the function func in parallel with the arguments in list_args and returns the output as a list.
    Args:
        func: function to be executed
        list_args: list of arguments to be passed to the function
        num_processes: number of processes in the multiprocessing pool (default is the number of available CPU cores)
        return_arg: boolean to return the arguments in the output list (default is False)
        save_job_ids: boolean to save the job ids in a json file (default is False)
        save_direc: directory to save the job ids (default is the current working directory)
    Returns:
        A list containing the output of each function call in the same order as the input arguments.
    '''
    if return_arg or save_job_ids:
        results = []
        with multiprocessing.Pool(processes=num_processes) as pool:
            for result in pool.imap(worker, [(arg, func) for arg in list_args]):
                results.append(result)
        if save_job_ids:
            runs_dic = {val:job_id for val, job_id in enumerate(results)}
            #save the runs_dic to a json file
            with open(f'{save_direc}/.runs_dic.json', 'w') as f:
                json.dump(runs_dic, f)
        if return_arg:
            return results
    else:
        pool = multiprocessing.Pool(processes=num_processes)
        if isinstance(list_args[0], tuple):  #function takes multiple arguments
            pool.starmap(func, list_args)
        else: #function takes a single argument
            pool.map(func, list_args)
        pool.close()
        pool.join()
        return




def mdisplay(dfs, names=[], index=False) -> None:
    '''
    displays multiple dataframes side by side.
    args: dfs --> list of dataframes, names --> list of names for the dataframes, index --> boolean to display the index
    '''
    if type(dfs) is dict:
        names = list(dfs.keys())
        dfs = list(dfs.values())
    def to_df(x):
        if isinstance(x, pd.Series):
            return pd.DataFrame(x)
        else:
            return x
    html_str = ''
    if names:
        html_str += ('<tr>' + 
                    ''.join(f'<td style="text-align:center">{name}</td>' for name in names) + 
                    '</tr>')
    html_str += ('<tr>' + 
                ''.join(f'<td style="vertical-align:top"> {to_df(df).to_html(index=index)}</td>' 
                        for df in dfs) + 
                '</tr>')
    html_str = f'<table>{html_str}</table>'
    html_str = html_str.replace('table','table style="display:inline"')
    display_html(html_str, raw=True)
    return


def sgn(x:float) -> int:
    if x<0:
        return -1
    else:
        return 1

def pdiff(e1, e2):
    '''returns the percentage difference between e1 and e2'''
    
    if isinstance(e1, (int, float)):
        e1 = np.array([e1])
    if isinstance(e2, (int, float)):
        e2 = np.array([e2])
    
    if len(e1) != len(e2):
        lent = min(len(e1), len(e2))
        e1 = e1[:lent]
        e2 = e2[:lent]
    e1 = np.asarray(e1)
    e2 = np.asarray(e2)
    mid = 0.5*(e1 + e2)
    diff = e1 - e2
    zero_mask = np.where((e1 == 0) & (e2 ==0))
    nonzero_mask = np.where((e1 != 0) | (e2 !=0))
    result = np.zeros_like(e1)
    result[nonzero_mask] = 100*diff[nonzero_mask]/mid[nonzero_mask]
    result[zero_mask] = 0
    if len(result) == 1:
        return result[0]
    else:
        return result

def read_file(infile:str) -> list:
    #reads a file with a single column of numbers and returns them as strings in a list
    with open(infile,'r') as file:
        lines = file.readlines()
    lines = [line.rstrip('\n') for line in lines]
    return lines


def symlink(src: str, dest_dir: str, symlink_name:str=None) -> None:
    '''
    Creates a symlink to the source file in the destination directory.

    Args:
        src (str): Path to the source file.
        dest_dir (str): Path to the destination directory.

    Returns:
        None
    '''
    # Check if source file exists
    assert os.path.exists(src), f'Error: {src} does not exist'
    assert os.path.isdir(dest_dir), f'Error: {dest_dir} does not exist'

    # Create symlink
    if symlink_name:
        dest = os.path.join(dest_dir, symlink_name)
    else:
        dest = os.path.join(dest_dir, os.path.basename(src))
    os.symlink(src, dest)
    return



def delete_files(directory_path):
    confirm = input(f"Are you sure you want to delete all files in '{directory_path}'? (y/n): ").strip().lower()

    if confirm == 'y':
        try:
            file_list = os.listdir(directory_path)
            for file_name in file_list:
                file_path = os.path.join(directory_path, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print("All files deleted successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("Deletion canceled.")
    return

def sgn(x):
    if x<0:
        return -1
    elif x==0:
        return 0
    else:
        return 1
    
def obtain_names(pwd:str) -> str:
    '''returns the name of the fixed variable from the print.py file'''
    file_name = '.variable_names'
    with open(os.path.join(pwd, file_name), 'r') as f:
        contents = f.read()
    match = re.search(r'tuning_var_name\s*=\s*(.*)', contents)
    assert match, f'tuning_var_name not found in {file_name}'
    tuning_var_name = match.group(1)
    match = re.search(r'fixed_var_name\s*=\s*(.*)', contents)
    assert match, f'fixed_var_name not found in {file_name}'
    fixed_var_name = match.group(1)
    dic = {'fixed_var_name': fixed_var_name.strip().replace('\'', ''), 'tuning_var_name':tuning_var_name.strip().replace('\'', '')}
    return dic


def new_SLURM_job(command:str, job_name:str, location:str, SLURM_file_name:str, time:str):
    '''creates a new SLURM job to the run the command from a specific location (mostly used for plotting)
    args
        command: command to be run
        job_name: name of the job
        location: location of the SLURM file
        SLURM_file_name: name of the SLURM file'''
    SLURM_string = \
f'''#!/bin/tcsh
#SBATCH --job-name={job_name}   # Job name
#SBATCH --mail-type=FAIL,END          # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --account=physics-dept
#SBATCH --qos=physics-dept
#SBATCH --partition=hpg-default
#SBATCH --ntasks=1
#SBATCH --mem=6Gb                     # Job memory request
#SBATCH --time={time}              # Time limit hrs:min:sec
#SBATCH --output={job_name}_script_output   # Standard output and error log
echo "Job ID: $SLURM_JOB_ID"
pwd; hostname; date
conda activate qim_coding_env
{command}
date'''
    with open(f'{location}/{SLURM_file_name}', 'w') as file:
        file.write(SLURM_string)
    return



        


