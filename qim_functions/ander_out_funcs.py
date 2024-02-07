import pandas as pd
import numpy as np
from .aextr import aextr
import re

def extract_level(infile, qno, par):
    '''
    extracts the level with qno=[sf,jf,index] from the output file as a function of iteration number.
    **arge: infile, qno=[sf,jf,index], par='even' for models with fermions and 'all' for the models without fermions.
    '''
    data_frame = aextr(infile, 3.0, par)
    condition = (data_frame['sf']==qno[0]) & (data_frame['jf']==qno[1]) & (data_frame['index']==qno[2])
    return data_frame[condition]

def extract_it(infile, it):
    '''
    extracts the levels at iteration number it from the output file.
    **arge: infile, it
    '''
    data_frame = aextr(infile, 3.0, 'all')
    condition = (data_frame['n']==it) & (data_frame['energy']<=3.0)
    return data_frame[condition]


def extract_excite(ander_out):
    var_lines = {}
    var_lines[1] =  ['excite', 'ediff', 'e2diff']
    var_lines[2] = ['bxcite', 'fxcite', 'fxsplit']
    var_lines[3] = ['islope', 'icurve', 'ireverse']
    var_lines[4] = ['lastit']
    # print([var_line1[0], var_line2[0], var_line3[0], var_line4[0]])
    vars = ['n'] + [var for var_line in var_lines.values() for var in var_line]
    return_dict = {var:[] for var in vars}
    with open(ander_out, 'r') as file:
        all_lines = file.readlines()

    row_ind = 0
    for line_ind, line in enumerate(all_lines): # Iterate over the lines in the file
        match_iter = re.match(r'Iteration number\s+(\d+)', line)  # Match iteration number
        if match_iter:
            current_iteration = int(match_iter.group(1))

        match_string = r'excite = ' 
        match = re.search(match_string, line)
        if match: #starting of the diagnostic lines
            #create a dummy row
            return_dict['n'].append(current_iteration)
            for var_string in vars[1:]:
                return_dict[var_string].append(np.nan)
                
            #start iterating over the diagnostic lines
            for k, var_line in enumerate(var_lines.values()):
                if 'D>' in all_lines[line_ind+k]: #there is diagnostic line
                    for var_string in var_line:
                        match_var = re.search(r'{}\s*=\s*([\d.E+-]+)'.format(var_string), all_lines[line_ind+k])
                        if match_var:
                            return_dict[var_string][row_ind] = float(match_var.group(1))
                            # print(current_iteration, k, var_string, return_dict[var_string])
            row_ind += 1    

    return_df = pd.DataFrame(return_dict)
    return return_df


def extract_ehi(ander_out):
    with open(ander_out, 'r') as file:
        lines = file.readlines()
    #obtain the maximum value of ehi
    E = []
    for line in lines:
        match = re.search(r'ehi\s*=\s*([\d.-]+)', line)
        if match:
            ehi = float(match.group(1))
            E.append(ehi)
    return max(E)



