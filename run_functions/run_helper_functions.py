import re
import os
import glob
import subprocess



#########################################################################
#Functions related to running calculation in blue:

# def extract_variable_values(path):
def obtain_variable_values(path):
    '''
    Looks for all directories of the form '{var}={value}' in the given path and returns the string 'var' and the list of 'value's.
    args: path
    returns: var-->string, values-->sorted list of values as strings
    '''
    regex_pattern = r'([^=]+)=([^/]+)$'
    directories = [name for name in os.listdir(path) if os.path.isdir(path)]
    var_names = []
    var_values = []
    for direc in directories:
        match = re.match(regex_pattern, direc)
        if match:
            var_name = match.group(1)
            var_value = match.group(2)
            if not var_name in var_names:
                var_names.append(var_name)
            var_values.append(var_value)
    # assert len(var_names) == 1, "Only one variable value is allowed"
    try:
        var_values.sort(key=float) # sort by numerical value
    except ValueError: #there are some strings in the list, so no need to sort it
        pass

    if len(var_names)==0: #no variable values found
        print('No variable values found')
        return 
    elif len(var_names) == 1: #Only one var present
        return var_names[0], var_values
    else:
        print('More than one variable found')
        return var_names, var_values

#obtain the list of numbers for ander.out in the present directoy
def obtain_outfiles(path):
    '''
    Returns the list of numbers for ander.out** in the present directoy.
    args: path
    returns: list of ** as strings'''
    file_names = glob.glob(os.path.join(path, "ander.out??"))
    ander_nums = [file_name.split('.')[-1] for file_name in file_names]
    return ander_nums

def read_file(infile):
    #reads a file with a single column of numbers and returns them as strings in a list
    with open(infile,'r') as file:
        lines = file.readlines()
    lines = [line.rstrip('\n') for line in lines]
    return lines


def input_check(params:dict, fixed_var_name:str) -> None:
    #checks if the thresholds for the find driver are set correctly
    assert params['var_min'] < params['var_max'], r'var_min must be less than var_max'
    inputs = ['ed', 'U', 'Gamma', 'Delta', 'g', 'K', 'var_min', 'var_max'] #neccecary inputs for ander.in
    inputs.remove(fixed_var_name) #removing the fixed variable. This should be set by the print script
    missing_inputs = [input for input in inputs if input not in params]
    assert len(missing_inputs)==0, fr'missing inputs: {missing_inputs}'
    return 


def assign_thresholds(tuning_var_name:str, energies:dict) -> dict:
    #assigns the thresholds for the find driver
    assert tuning_var_name in ['ed', 'U', 'Gamma', 'g'], 'tuning_var_name must be one of ed, U, Gamma, g'
    if tuning_var_name in ['ed', 'g']:
        dreneg = energies['delocalized_energy']
        drepos = energies['localized_energy']
    elif tuning_var_name in ['Gamma']:
        dreneg = energies['localized_energy']
        drepos = energies['delocalized_energy']
    return dreneg, drepos

def wrun():
    ''' runs the ~/wrun.csh script'''
    subprocess.run(['bash', '/home/an.kandala/wrun.csh'])
    return


def write_var_names(pwd:str, tuning_var_name:str, fixed_var_name:str) -> None:
    '''writes the tuning_var_name and fixed_var_name to a file'''
    with open(os.path.join(pwd, '.variable_names'), 'w') as f:
        f.write(f'tuning_var_name = {tuning_var_name}\n')
        f.write(f'fixed_var_name = {fixed_var_name}\n')
    return