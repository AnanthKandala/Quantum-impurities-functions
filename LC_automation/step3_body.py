import subprocess
import os
from .step3_plotting_funcs import plot_all_runs
from .step3_extract import extract_ediff




def step3(nb, s, num_cpu_plot):
    pwd = os.getcwd()
    # find_edc_direc = fr'{pwd}/runs_data_base/s={s}/nb={nb}/find_edc_runs'
    #running psr and gspec codes:
    # subprocess.run(['python', '/orange/physics-dept/an.kandala/custom_python_modules/run_functions/g_spec.py'], check=True, stdout=subprocess.PIPE,  cwd=find_edc_direc)

    fixed_var_name = 'g'
    tuning_var_name = 'ed'
    path_blue = fr'{pwd}/runs_data_base/s={s}/nb={nb}/find_edc_runs'
    #obtain the shift in the ground state energy:
    ec, ec_error = extract_ediff(path_blue, fixed_var_name)

    #plot find_runs:
    out_direc = fr'/orange/physics-dept/an.kandala/proper_research/Level_crossing/automated_runs/s={s}/nb={nb}/find_edc_runs'
    par = 'all'
    plot_all_runs(fixed_var_name, tuning_var_name, path_blue, out_direc, par, s, nb, num_cpu_plot)
    print(f'finished nb={nb}, s={s}')
    return (ec, ec_error)


