import pandas as pd

def log_couplings(infile):
    '''
    extracts the best estimates of the critical coupling from the ander.log file'''
    with open(infile, "r") as f:
        all_lines = f.readlines()
    last_line = all_lines[-1]
    var_min = float(last_line.split()[-2])
    var_max = float(last_line.split()[-1])
    return [var_min, var_max]

def get_last_runs(log_file):
    '''
    extracts the indices of the runs closest to the critical point from the log file'''
    log_frame = pd.read_csv(log_file,sep=r'\s+')
    phases = log_frame['phase'].unique()
    num_phases = len(phases)
    phase_boundary = {}
    if num_phases == 0:
        return phase_boundary
    else:
        for phase in phases:
            phase_boundary[phase] = log_frame[log_frame['phase']==phase].iloc[-1]['run_index']
        return phase_boundary
    
