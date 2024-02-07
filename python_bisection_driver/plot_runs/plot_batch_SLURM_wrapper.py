from qim_functions import new_SLURM_job
from run_functions import launch_slurm_script
import os


if __name__ == '__main__':
    command = 'python /orange/physics-dept/an.kandala/custom_python_modules/python_bisection_driver/plot_runs/plot_run_batch.py'
    job_name = 'python_bisection_plotting'
    location = os.getcwd()
    SLURM_file_name = 'SLURM_plotting'
    time = '01:00:00'
    new_SLURM_job(command, job_name, location, SLURM_file_name, time)
    launch_slurm_script(location, SLURM_file_name)
