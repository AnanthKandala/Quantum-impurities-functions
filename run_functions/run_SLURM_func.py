import subprocess

#prints SLURM script:
def write_slurm_script(title: str, directory: str, run_time: str, find_run=False) -> None:
    '''
    Writes a SLURM script to {directory}/SLURM.

    Args:
        title (str): Job name.
        directory (str): Directory to write the SLURM script to.
        run_time (str): Time limit in the format 'hh:mm:ss'.
    '''
    if find_run:
        SLURM_string = \
f'''#!/bin/tcsh
#SBATCH --job-name={title.replace(" ", "")}   # Job name
#SBATCH --mail-type=FAIL,END          # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --account=physics-dept
#SBATCH --qos=physics-dept
#SBATCH --ntasks=1                    # Run on a single CPU
#SBATCH --mem=1Gb                     # Job memory request
#SBATCH --time={run_time}               # Time limit hrs:min:sec
#SBATCH --output=script_output   # Standard output and error log
echo "Job ID: $SLURM_JOB_ID"
pwd; hostname; date
# Load modules
module load gcc/12.2.0
module load lapack/3.11.0
# Run command
{directory}/ander
date
conda activate qim_coding_env
python /orange/physics-dept/an.kandala/custom_python_modules/run_functions/single_gspec.py
echo calculation complete!'''
    else:
        SLURM_string = \
f'''#!/bin/tcsh
#SBATCH --job-name={title.replace(" ", "")}   # Job name
#SBATCH --mail-type=FAIL,END          # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --account=physics-dept
#SBATCH --qos=physics-dept
#SBATCH --ntasks=1                    # Run on a single CPU
#SBATCH --mem=1Gb                     # Job memory request
#SBATCH --time={run_time}               # Time limit hrs:min:sec
#SBATCH --output=script_output   # Standard output and error log
echo "Job ID: $SLURM_JOB_ID"
pwd; hostname; date
# Load modules
module load gcc/12.2.0
module load lapack/3.11.0
# Run command
{directory}/ander
date
echo calculation complete!'''

    with open(f'{directory}/SLURM', 'w') as file:
        file.write(SLURM_string)
    return


def launch_slurm_script(slurm_dir:str, file_name='SLURM'):
    # Use sbatch to submit the SLURM script and capture the output
    result = subprocess.run(['sbatch', file_name], check=True, stdout=subprocess.PIPE,  cwd=slurm_dir)
    output = result.stdout.decode('utf-8')
    line = output.strip()
    job_id = line.split()[-1]
    print(line, job_id)
    return job_id