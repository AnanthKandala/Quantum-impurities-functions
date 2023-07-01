import re
import pandas as pd
import numpy as np



def aextr(filename, max_energy, par):
    '''
    inputs = (filename, max_energy, par)
    filename: name of the file to be read
    max_energy: maximum energy to be considered
    par: parity of the levels to be considered
    outputs a dataframe with the levels and a status string
    '''
    #Obtain all the levels from the file at each iteration
    all_levels = []
    all_iterations = []  # Open the file and read its content
    with open(filename, 'r') as file:
        for line in file: # Iterate over the lines in the file
            match_iter = re.match(r'Iteration number\s+(\d+)', line)  # Match iteration number
            if match_iter:
                current_iteration = int(match_iter.group(1))
                all_iterations.append(current_iteration)
            # Match state information
            basic_string = r'(\d+)\s+([-+]?\d*\.\d+|\d+)\s+([-+]?\d+)\s+(\d+)\s+([-+]?\d+)\s+(\d+)\s+(\d+)'
            matches = re.finditer(basic_string, line)
            levels_line = [line.group().split() for line in matches]
            for match in levels_line:
                if float(match[1]) < max_energy:
                    all_levels.append(tuple([str(current_iteration)]) + tuple(match)[1:])

    columns = ['n', 'energy', 'sf', 'sg', 'jf', 'jg', 'P', 'index']
    levels_dic = {col:[] for col in columns}
    row_ind = 0
    if par=='even':
        iterations = [i for i in all_iterations if i%2==0]
    elif par=='odd':
        iterations = [i for i in all_iterations if i%2==1]
    else:
        iterations = all_iterations

    for it in iterations:
        levels_it = [level for level in all_levels if int(level[0]) == it]
        energies = [float(level[1]) for level in levels_it]
        sorted_indices = np.argsort(energies)
        counts = {}
        for i in sorted_indices:
            level = levels_it[i]
            # calcualted the count of the level
            if level[2:] not in counts:
                counts[level[2:]] = 1
            else:
                counts[level[2:]] += 1
            #populate the dictionary
            levels_dic['n'].append(str(it))
            levels_dic['energy'].append(level[1])
            for j in range(2, 7):
                levels_dic[columns[j]].append(level[j])
            levels_dic['index'].append(str(counts[level[2:]]))
            row_ind += 1
    if len(all_levels)!= row_ind:
        status = 'failed'
    else:
        status = ''
    levels_df = pd.DataFrame(levels_dic)
    return levels_df, status



def ander_in(infile, driver):
    '''
    Extracts the parameters from the ander.in file and returns them as a dictionary.
    '''
    if driver == 'standard':
        n0 = 0
        with open(infile, "r") as ff:
            Aa = ff.readlines()

        Bb = Aa[n0].split()
        ed = round(float(Bb[0]), 7)
        U = Bb[1]
        Gamma = Bb[2]
        c = Aa[1][2].split()
        if float(U) != 0.0:
            eta = 2.0 * ed / float(U) + 1
        else:
            eta = 'Nan'
        delta = float(Aa[n0 + 3].split()[0])
        g = float(Aa[n0 + 1].split()[2])

        parameters = {
            'ed': ed,
            'U': U,
            'eta': eta,
            'Gamma': Gamma,
            'delta': delta,
            'g': g
        }
    return parameters

    # elif driver == 'find':
    #     n0 = 2