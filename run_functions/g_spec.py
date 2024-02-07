import os
from run_check import run_check_func
from g_spec_func import process_run_dir
from qim_functions import parallel

#tcsh shell script that runs process() function for calculations that have been deemed to have converged
pwd = str(os.getcwd())
print(pwd)
#run run_check to identify which runs have converged
completed_runs = run_check_func(pwd)
os.system('echo "ran run_check.py"')
#gspec on the runs that have converged paralelly:
directory_names = [f'{pwd}/{direc}' for direc in completed_runs['index']]
parallel(process_run_dir, directory_names)

