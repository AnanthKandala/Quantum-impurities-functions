#date created: 
#last updated: 2 August 2023

import os
import subprocess
from run_functions import obtain_variable_values

pwd = os.getcwd()

# Obtain variable values from the current directory
var_name, var_values = obtain_variable_values(pwd)
with open('running_var1.txt', 'w') as f:
    for var in var_values:
        f.write(var + '\n')

# Check for nested directories
direc = f'{pwd}/{var_name}={var_values[0]}'
var_name2, var_values2 = obtain_variable_values(direc)

if type(var_name) == str:
    with open('running_var2.txt', 'w') as f:
        for var in var_values2:
            f.write(var + '\n')


combos = [(v1, v2) for v1 in var_values for v2 in var_values2]
count = 0
for combo in combos:
    slurm_dir = f'{pwd}/{var_name}={combo[0]}/{var_name2}={combo[1]}'
    if os.path.isdir(slurm_dir):
        try:
            subprocess.run(['sbatch', 'SLURM'], check=True, cwd=slurm_dir)
            count += 1
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while submitting the SLURM job in directory {slurm_dir}. Details: {e}")
    else:
        print(f"Directory {slurm_dir} does not exist.")
print(f"Submitted {count} SLURM jobs.")
# combos = [(v1, v2) for v1 in var_values for v2 in var_values2]
# for combo in combos:
#     slurm_file = f'{pwd}/{var_name}={combo[0]}/{var_name2}={combo[1]}'
#     os.system(f'cd {slurm_file} && sbatch slurm.sh')
#     os.system(f'cd {pwd}')
    
    # subprocess.run(['sbatch', slurm_file])
    
#     # Construct the tcsh script string
#     script_string = f"""#!/bin/tcsh

# # Read the values from running_var1.txt and running_var2.txt
# set var1_list = `cat running_var1.txt`
# set var2_list = `cat running_var2.txt`

# # Generate Cartesian product of var1 and var2
# set combinations = `python -c "import itertools; import ast; var1_list=ast.literal_eval('$var1_list'); var2_list=ast.literal_eval('$var2_list'); print(list(itertools.product(var1_list, var2_list)))"`

# # Loop over all combinations
# foreach combination ($combinations)

#     # Get the var1 and var2 values from the current combination
#     set var1 = $combination[1]
#     set var2 = $combination[2]

#     # Construct the path using the current var1 and var2 values
#     set directory_path = "{pwd}/{var_name}=$var1/{var_name2}=$var2"

#     # Change to the target directory
#     cd $directory_path

#     # Echo the current var1 and var2 values
#     echo "var1: $var1, var2: $var2"

#     # Submit the batch job using sbatch with SLURM script
#     sbatch SLURM

#     # Go back to the original directory after the job submission
#     cd -
# end
# """

#     with open('launch.sh', 'w') as f:
#         f.write(script_string)
    
#     # Make the shell script executable
#     subprocess.run(["chmod", "+x", "launch.sh"])

#     # If you wish to automatically execute the shell script, uncomment the line below
#     # subprocess.run(["tcsh", "launch.sh"])

#     # If you wish to remove the shell script after execution, uncomment the line below
#     # os.remove("launch.sh")

#     # Execute another shell script, if needed
#     # result = subprocess.run(["bash", "~/wrun.sh"], capture_output=True, text=True)
#     # print(result.stdout)
#     # print(result.stderr)
# else:
#     print('No nested directories')
