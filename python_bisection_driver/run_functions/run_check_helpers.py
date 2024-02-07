import pandas as pd
import numpy as np
import subprocess
import os
import json
import re

def get_slurm_job_state(run_path):
    '''obtains the job state for a job launched from run_path
    args:
        run_path [str]: the run directory
    returns:
        job_state [str]: the SLURM job state'''
    if not os.path.isfile(f'{run_path}/script_output'):
        return 'no script_output file found'
    else:
        SLURM_output_lines = open(f'{run_path}/script_output').readlines()
        # find a line that looks like Job ID: $SLURM_JOB_ID using re and extract the job id
        is_job_in = False
        for line in SLURM_output_lines:
            if 'Job ID' in line:
                is_job_in = True
                break
        if not is_job_in:
            return 'no job id found'
        else:
            job_id = re.findall(r'Job ID: (\d+)', line)
            job_id = job_id[0]
            try:
                # Run the sacct command and capture its output
                command = ['sacct', '-j', job_id, '--format=State', '--noheader']
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

                # Extract the job state from the output
                job_state = result.stdout.strip().split('\n')[-1].split()[-1]

                # Check if the job state is valid
                # valid_states = ['PENDING', 'RUNNING', 'SUSPENDED', 'COMPLETING', 'COMPLETED', 'CANCELLED', 'FAILED', 'TIMEOUT', 'NODE_FAIL', 'PREEMPTED']
                # if job_state in valid_states:
                return job_state
            except subprocess.CalledProcessError as e:
                return f"Error: {e}"
    

def status_string(run_direc, path_blue):
    slurm_status = get_slurm_job_state(f'{path_blue}/{run_direc}')
    if os.path.isfile(f'{path_blue}/{run_direc}/convg_failed'):
        #only 1 phase found in the first 8 iterations, so the run was stopped.
        slurm_status = f'{slurm_status} [convg_failed]'
    log_file = f'{path_blue}/{run_direc}/ander.log'
    if os.path.isfile(log_file): #logfile found
        if os.path.getsize(log_file) == 0: #empty logfile
            status_string = f'{run_direc} | {slurm_status} | empty log file!'
        else: #non-empty logfile
            log_frame = pd.read_csv(log_file,sep=r'\s+')
            phases = log_frame['phase'].unique()
            convert = {'delocalized': 'Deloc', 'localized': 'Loc'}
            phases_string = []
            for phase in phases:
                phases_string.append(f"{convert[phase]}[{len(log_frame[log_frame['phase'] == phase])}]")
            phases_print = ', '.join(phases_string)
            couplings = log_frame.iloc[-1][['min_var', 'max_var']].to_numpy()
            diff = log_frame.iloc[-1]['diff']
            if slurm_status == 'COMPLETED': #calculation converged and is complete
                status_string = f'{run_direc} | {slurm_status} | {phases_print}, diff={diff} | {np.average(couplings)}'
            else: #calculation is converging but still running
                status_string = f'{run_direc} | {slurm_status} | {phases_print}, diff={diff} | {couplings}'
    else: #no logfile found
        status_string = f'{run_direc} | {slurm_status} | no log file!'
    return status_string

    
