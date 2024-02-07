from run_functions import create_run_dir, write_slurm_script
import os
import subprocess
import time

def write_in(f,ed,U,Gamma, Delta,g, K) -> None:
    with open(f, 'w') as file1:
         file1.write(f'{ed} {U} {Gamma}  0.0    0.0    0.0'+'\n')
         file1.write(f'0.0    0.0    {g}    0.0    0.0    1.0      0'+'\n')
         file1.write('0.0    0.0    0.0    0.0    0.0    0.0    0.0'+'\n')
         file1.write(f'{Delta}    0.0    0.0    0.0                          1'+'\n')
         file1.write('9.0    0.0    0.0          1d-6         1d-20'+'\n')
         file1.write(f'0     25      0   {K}      0      1      0     0'+'\n')
         file1.write('5    0.6'+'\n')
    return

def init_run_dir(path:str,nb:int, s:float, r:float, ander_data) -> None:
    '''creates a directory with ander, ander.band/bath and ander.data files '''
    ander_exec = r'1000.1_flocal_-1:15_4September2023'
    files = {'ander': ander_exec, 'ander.data': ander_data}
    create_run_dir(path, files, s, r, clear_directory=False)
    return 

def single_run(run_direc, run_count, nb, s, params, ander_data):
    r = None
    title = f'{os.path.split(run_direc)[1]}' #title for the slurm script

    if os.path.isfile(f'{run_direc}/ander.out'): 
        os.rename(f'{run_direc}/ander.out', f'{run_direc}/ander.out{run_count-1}') #rename the ander.out file
    
    if run_count == 0: #first run: need to make run directory and write slurm script
        init_run_dir(run_direc, nb, s, r, ander_data) #initialize the run directory
    run_time = '14:30:00'
    # write_slurm_script(title,run_direc, run_time) #write the slurm script
    write_in(f'{run_direc}/ander.in', **params) #write the ander.in file
    command = f'{run_direc}/ander'
    try:
        subprocess.run(command, check=True, shell=True, executable='/bin/tcsh')
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    # slurm_script_command = ['sbatch', f'SLURM']
    # # Start the SLURM script as a subprocess
    # process = subprocess.Popen(slurm_script_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=run_direc)
    # # Wait for the subprocess to complete and capture the return code
    # # process.wait()
    # slurm_output = process.stdout.read().decode('utf-8')
    # job_id = slurm_output.strip().split()[-1]
    # Monitor the job's status
    # while True:
    #     check_status_command = ['sacct', '-j', job_id]
    #     status_process = subprocess.Popen(check_status_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     # status_process.wait()
    #     status_output = status_process.stdout.read().decode('utf-8')
    #     # Check if the job has completed (look for 'COMPLETED' status)
    #     if 'COMPLETED' in status_output:
    #         print(f"Slurm job {run_count} has completed.")
    #         break
    #     # Check if the job has failed (look for 'FAILED' status)
    #     if 'FAILED' in status_output:
    #         print(f"Slurm job {run_count} has failed.")
    #         break
    #     # If the job is still running, wait for a while before checking again
    #     time.sleep(15)  # Wait for 1 second (adjust as needed)
    return


