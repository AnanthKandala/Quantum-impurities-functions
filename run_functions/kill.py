import json
import os

def cancel_jobs(var_cancel=None):
    #read the dictionary of runs:
    with open('.runs_dic.json', 'r') as f:
        runs_dic = json.load(f)
    if var_cancel is None:
        var_cancel = runs_dic.keys()
    user_input = input(f"Do you want to stop : {','.join(map(str,var_cancel))}? (y/n):").strip().lower()
    if user_input == "y":
        for var in var_cancel:
            try:
                job_id = runs_dic[var]
                os.system(f'scancel {job_id}')
                print(f'cancelled job_id={job_id}, {var}')
            except:
                print(f'job_id={job_id} not found')
    else:
        print("No jobs cancelled")
    return


if __name__ == '__main__':
    #read the job ids:
    var_cancel = None
    # var_cancel = range(2, 40)
    cancel_jobs(var_cancel)
    
