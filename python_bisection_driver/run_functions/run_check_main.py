from python_bisection_driver.run_functions.run_check_helpers import status_string
from python_bisection_driver.qim_functions.misc_funcs import obtain_names
from run_functions import obtain_variable_values
import multiprocessing
import os
from natsort import natsort_keygen
import json
import time

if __name__ == "__main__":
    pwd = os.getcwd()
    natsort_key = natsort_keygen()
    directories = [name for name in os.listdir(pwd) if '=' in name]
    assert len(directories) > 0, 'No run directories found'
    directories.sort(key=natsort_key)
    # with open('.runs_dic.json', 'r') as f:
    #         job_dictionary = json.load(f)
    input_args = [(direc, pwd) for direc in directories]
    #measure the time it takes to run the code
    start_time = time.time()
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        STATUS = pool.starmap(status_string, input_args)
    # STATUS = [i for i in results]
    print('\n')
    with open('STATUS.txt', 'w') as f:
        f.write('\n'.join(STATUS))
    end_time = time.time()
    print('Total time taken: ', end_time - start_time)
    os.system('cat STATUS.txt')
    print('\n')
