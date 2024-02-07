import os
from run_functions import obtain_variable_values

pwd = os.getcwd()
# print(pwd)


var_name, var_values = obtain_variable_values(pwd)


with open('running_var.txt', 'w') as f:
    for var in var_values:
        f.write(var + '\n')

script_string = f"""#!/bin/tcsh
set var = `cat running_var.txt`
foreach var ($var)
    cd "{pwd}/{var_name}=$var"
    sbatch SLURM
end"""
with open('launch.sh', 'w') as f:
    f.write(script_string)
os.system('tcsh launch.sh')
os.system('rm launch.sh')
os.system('bash ~/wrun.sh')

# import subprocess
# result = subprocess.run(["bash", "-c", "bash ~/wrun.sh"], shell=True, capture_output=True, text=True)
# print(result.stdout)
# print(result.stderr)