import os
import re


def obtain_names(pwd:str) -> str:
    '''returns the name of the fixed variable from the print.py file'''
    file_name = '.variable_names'
    with open(os.path.join(pwd, file_name), 'r') as f:
        contents = f.read()
    match = re.search(r'tuning_var_name\s*=\s*(.*)', contents)
    assert match, f'tuning_var_name not found in {file_name}'
    tuning_var_name = match.group(1)
    match = re.search(r'fixed_var_name\s*=\s*(.*)', contents)
    assert match, f'tuning_var_name not found in {file_name}'
    fixed_var_name = match.group(1)
    return fixed_var_name.strip().replace('\'', ''), tuning_var_name.strip().replace('\'', '')