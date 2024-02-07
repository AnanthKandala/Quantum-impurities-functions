import os
from run_functions import run_check_func, process_run_dir

if __name__ == '__main__':
    pwd = str(os.getcwd())
    print(pwd)
    process_run_dir(pwd) #process the run directory
    
    # parent_dir = os.path.dirname(pwd)
    # run_check_func(parent_dir) #run the run_check function on the parent directory

