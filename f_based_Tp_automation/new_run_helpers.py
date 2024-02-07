from run_functions import create_run_dir

#prints SLURM script:
def write_slurm_script(title: str, directory: str, run_time: str) -> None:
    '''
    Writes a SLURM script to {directory}/SLURM.

    Args:
        title (str): Job name.
        directory (str): Directory to write the SLURM script to.
        run_time (str): Time limit in the format 'hh:mm:ss'.
    '''
    SLURM_string = \
f'''#!/bin/tcsh
#SBATCH --job-name=[fscore]{title.replace(" ", "")}   # Job name
#SBATCH --mail-type=FAIL,END          # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --account=physics-dept
#SBATCH --qos=physics-dept
#SBATCH --ntasks=1                    # Run on a single CPU
#SBATCH --mem-per-cpu=10Gb                     # Job memory request
#SBATCH --time={run_time}               # Time limit hrs:min:sec
#SBATCH --output=script_output   # Standard output and error log
pwd; hostname; date
# Load modules
module load gcc/12.2.0
module load lapack/3.11.0
# Run command
{directory}/ander
echo calculation complete!
date
conda activate qim_coding_env
python /orange/physics-dept/an.kandala/custom_python_modules/run_functions/single_gspec.py
python /orange/physics-dept/an.kandala/custom_python_modules/f_based_Tp_automation/main.py
sstat --format='JobID,MaxRSS,AveCPU' -P ${{SLURM_JOB_ID}}.batch >> job.stats'''
    with open(f'{directory}/SLURM', 'w') as file:
        file.write(SLURM_string)
    return



#prints ander.in
def write_in(infile, ed, U, Gamma, g, K, var_min, var_max, dreneg, drepos) -> None:
    string = \
f'''{var_min} {var_max} 1d-13    100
    6      0   {dreneg} {drepos}     -3
    {ed} {U} {Gamma}  0.0    0.0    0.0
    0.0    0.0    {g}    0.0    0.0    1.0      0
    0.0    0.0    0.0    0.0    0.0    0.0    0.0
    0.0   0.0    0.0    0.0                          1
    9.0    0.0    0.0          1d-6         1d-20
    0     60      0   {K}      0      1      0     0
    5    0.6'''
    with open(infile, 'w') as file1:
        file1.write(string)
    return


    
def init_run_dir(path:str, nb, s, r:None) -> None:
    '''creates a directory with ander, ander.band/bath and ander.data files '''
    ander_exec = r'find_Gammac_bfam.1000:15_Dec72023'
    ander_data = fr'nb_testing_local_fmodel/ph_asym/1_-1:{nb}.data'
    files = {'ander': ander_exec, 'ander.data': ander_data}
    create_run_dir(path, files, s, r)
    return 
