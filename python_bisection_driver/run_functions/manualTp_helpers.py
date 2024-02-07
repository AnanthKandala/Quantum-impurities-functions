from .single_run import single_run
from .calculate_phase import calculate_phase
import os


def find_phase(run_direc, run_count, in_params:dict, nb:int, s:float, ander_out) -> str:
    #perform a single run:
    single_run(run_direc, run_count, nb, s, in_params, ander_out)
    phase = calculate_phase(s, f'{run_direc}/ander.out')
    return phase

