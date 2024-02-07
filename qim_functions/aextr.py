import re
import pandas as pd
import numpy as np


#Functions to process the output of the ander program
def aextr(filename, max_energy, par):
    '''
    inputs = (filename, max_energy, par)
    filename: name of the file to be read
    max_energy: maximum energy to be considered
    par: parity of the levels to be considered ['even', 'odd', 'all']
    outputs a dataframe with the levels and a status string
    column_headers = ['n', 'energy', 'sf', 'sg', 'jf', 'jg', 'P', 'index']
    '''
    assert par in ['even', 'odd', 'all'], 'par must be one of [even, odd, all]'
    #Obtain all the levels from the file at each iteration
    all_levels = []
    with open(filename, 'r') as file:
        for line in file: # Iterate over the lines in the file
            match_iter = re.match(r'Iteration number\s+(\d+)', line)  # Match iteration number
            if match_iter:
                current_iteration = int(match_iter.group(1))
                # all_iterations.append(current_iteration)
            # Match state information
            basic_string = r'(\d+)\s+([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)\s+([-+]?\d+)\s+(\d+)\s+([-+]?\d+)\s+(\d+)\s+(\d+)'
            matches = re.finditer(basic_string, line)
            levels_line = [line.group().split() for line in matches]
            for match in levels_line:
                # energy, sf, sg, jf, jg, P = match[1:]
                all_levels.append([current_iteration] + match[1:])

    columns = ['n', 'energy', 'sf', 'sg', 'jf', 'jg', 'P', 'index']
    levels_dic = {col: [] for col in columns}
    all_iterations = np.unique([level[0] for level in all_levels])
    if par=='even':
        iterations = [i for i in all_iterations if i%2==0]
    elif par=='odd':
        iterations = [i for i in all_iterations if i%2==1]
    else:
        iterations = all_iterations

    for it in iterations:
        states_it = [level for level in all_levels if int(level[0]) == it] #all the states in the current iteration
        energies = [float(state[1]) for state in states_it] #all the energies in the current iteration
        sorted_indices = np.argsort(energies)
        counts = {}
        for i in sorted_indices:
            level = states_it[i]
            qno = tuple(level[2:])
            # calcualted the index of the level
            if qno not in counts:
                counts[qno] = 0
            else:
                counts[qno] += 1
            #populate the dictionary
            levels_dic['n'].append(it)
            levels_dic['energy'].append(float(level[1]))
            for j in range(2, 7):
                levels_dic[columns[j]].append(int(level[j]))
            levels_dic['index'].append(counts[qno])
    levels_frame = pd.DataFrame(levels_dic).sort_values(by=['n', 'energy'])

    #select all the levels with energy < emax at any iteration:
    cut_off_levels = pd.DataFrame({col: [] for col in levels_frame.columns})
    unique_qno = levels_frame[['sf', 'sg', 'jf', 'jg', 'P', 'index']].drop_duplicates()[['sf', 'sg', 'jf', 'jg', 'P', 'index']]
    for sf, sg, jf, jg, P, index in unique_qno.itertuples(index=False):
        query = f'sf=={sf} and sg=={sg} and jf=={jf} and jg=={jg} and P=={P} and index=={index}'
        level = levels_frame.query(query)
        if np.any(level['energy'].astype(float) < max_energy): #if any of the energies is below max_energy
            cut_off_levels = pd.concat([cut_off_levels, level])
    cut_off_levels = cut_off_levels.sort_values(by=['n', 'energy'])
    integer_columns = ['n', 'sf', 'sg', 'jf', 'jg', 'P', 'index']
    cut_off_levels[integer_columns] = cut_off_levels[integer_columns].astype(int)
    return cut_off_levels


