import numpy as np
import pandas as pd
from .aextr import aextr
from .thermo_funcs import n_crit
from .misc_funcs import pdiff
import os

def get_flat_bosonic_levels(spectrum, num_levels=1, return_tol=False):
    '''
    Returns the bosonic levels at the flattest iteration. Flattest iteration decided using the num_levels lowest bosonic excitations.
    **args: data_frame: pandas dataframe with all the levels
    **returns: pandas dataframe with the bosonic levels at the flattest iteration
           and the tolerance of the lowest bosonic excitation energy and the iteration at which it occurs.
    '''
    level_indices = np.arange(1, num_levels+1)
    flat_its = np.empty(num_levels)
    critical_energies = np.empty(num_levels)
    condition_dic1 = {'sf': 0, 'jf': 0}
    for i, index in enumerate(level_indices):
        condition_dic1['index'] = index
        condition = ' & '.join([f'{k} == {v}' for k, v in condition_dic1.items()])
        level = spectrum.query(condition)
        flat_its[i] = n_crit(level)
        assert ~np.isnan(flat_its[i]), f'Level {index} does not reach criticality'
        critical_energies[i] = float(level.query(f'n == {flat_its[i]}')['energy'].iloc[0])
    unique_flat_its, counts = np.unique(flat_its, return_counts=True)
    n_flat = unique_flat_its[np.argmax(counts)]
    unique_flat_its, counts = np.unique(flat_its, return_counts=True)
    n_flat = unique_flat_its[np.argmax(counts)] #most levels reach their critical values at this iteration
    condition_dic2 = {'sf': 0, 'jf': 0, 'n': n_flat}
    condition = ' & '.join([f'{k} == {v}' for k, v in condition_dic2.items()])
    flat_bosonic_levels = spectrum.query(f'n == {n_flat}')
    e_crit = [flat_bosonic_levels.query(f'index == {index}')['energy'].iloc[0] for index in level_indices]
    e_diff = np.abs(pdiff(e_crit, critical_energies))
    convg_tol = 1
    condition_tolerance = e_diff < convg_tol #all levels have reached criticality within a convg_tol
    if np.all(condition_tolerance):
        if return_tol:
                tolerance = np.empty(num_levels)
                condition_dic3 = {'sf': 0, 'jf': 0}
                for i, index in enumerate(level_indices):
                    condition_dic3['index'] = index
                    condition = ' & '.join([f'{k} == {v}' for k, v in condition_dic3.items()])
                    level = spectrum.query(condition)
                    energies = level.query(f'abs(n - {n_flat}) < 2 ')['energy'].to_numpy()
                    tolerance[i] = 100*(np.max(energies) - np.min(energies))/ np.average(energies)
                return flat_bosonic_levels, np.average(tolerance)
        else:
                return flat_bosonic_levels
    else:
        non_converged_levels = level_indices[~condition_tolerance]
        if isinstance(non_converged_levels, int):
            print(f"Level {non_converged_levels} has not reached criticality within a tolerance of {convg_tol}%")
            print(f"Level {non_converged_levels} has a tolerance of {e_diff[~condition_tolerance]}%")
        else:
            print(f"Levels {','.join(non_converged_levels.astype(str))} have not reached criticality within a tolerance of {convg_tol}%")
            print(f"Levels {','.join(non_converged_levels.astype(str))} have a tolerances {','.join(e_diff[~condition_tolerance].astype(str))}%")
    return


def get_critical_bosons(ander_file, par, phsym, return_tol=False):
    '''
    Returns the critcal bosonic levels at the flattest iteration. Flattest iteration decided using the lowest bosonic excitation.
    for the BFA model, it checks if the spectrum decomposes into ferimions times bosons. Critical bosons should appear in odd and even iterations.
    **args: data_frame: pandas dataframe with all the levels, par: 'even' for models with fermions and 'all' for the models without fermions.
    **returns: pandas dataframe with the bosonic levels at the (even) flattest iteration.
         if return_tol=True, it also returns the flatness tolerance at even and odd iterations.
    '''
    assert os.path.isfile(ander_file), f'{ander_file} does not exist'
    if par=='even': #obtain the bosonic levels at even iterations
        if phsym:
            Jfvalues = [1]
        else:
            Jfvalues = [-1, 1]
        #obtain flat bosonic levels at even iterations:
        even_levels = aextr(ander_file, 3.0, 'even')
        flat_bosonic_levels_even, tol_even = get_flat_bosonic_levels(even_levels, return_tol=True)

        #obtain flat bosonic levels at odd iterations:
        odd_levels = aextr(ander_file, 9.0, 'odd')
        flat_bosonic_levels_odd, tol_odd = get_flat_bosonic_levels(odd_levels, return_tol=True)

        #obtain even bosons that are present in odd iterations:
        condition = [np.min(np.abs(flat_bosonic_levels_odd['energy'] - 3*e))<0.1 for e in flat_bosonic_levels_even['energy']]    
        tol = 0.1 #Tolerance is set to less than tol percent

        test1_status = [True]*len(flat_bosonic_levels_even)
        test2_status = [True]*len(flat_bosonic_levels_even)
        n_flat = flat_bosonic_levels_even['n'].values[0] #iteration at which the bosons are flattest (even iterations)
        flat_even_levels = even_levels[even_levels['n']==n_flat]
        for i in range(1, len(flat_bosonic_levels_even)):
            e_b = flat_bosonic_levels_even['energy'].values[i]

            #check if the boson is present in the odd iterations:
            diff = np.min(np.abs(100*(flat_bosonic_levels_odd['energy'] - 3*e_b)/ (flat_bosonic_levels_odd['energy'] + 3*e_b)))
            test1_status[i] = diff<tol
        
        critical_bosonic_levels = flat_bosonic_levels_even[test1_status]
        for e_b in critical_bosonic_levels['energy']:
            #check for the presence of a combination with particle-like and hole-like excitations:
            sf_g = flat_bosonic_levels_even['sf'].values[0]
            jf_g = flat_bosonic_levels_even['jf'].values[0]
            status = []
            for k, jf in enumerate(Jfvalues):
                condition = (flat_even_levels['jf']==jf+jf_g) & (flat_even_levels['index']==0) & (flat_even_levels['sf']==1+sf_g)
                e_fermi = flat_even_levels[condition]['energy'].values[0]
                et = e_b + e_fermi
                condition = (flat_even_levels['jf']==jf+jf_g) & (flat_even_levels['sf']==1+sf_g) & (flat_even_levels['index']>0)
                fermionic_excitaitons = flat_even_levels[condition]
                status += np.min(np.abs(100.0*(fermionic_excitaitons['energy'] - et)/(fermionic_excitaitons['energy'] + et)))<tol 
            if not np.all(status==True):
                print('found an inconsistant boson that does not have composite excitations')
                return
    else: #obtain flat bosonic levels from all iterations
        all_levels = aextr(ander_file, 3.0, 'all')
        try:
            flat_bosonic_levels, tol = get_flat_bosonic_levels(all_levels, return_tol=True)
            critical_bosonic_levels = flat_bosonic_levels
        except:
            return
    
    if return_tol:
        diags = {'even_it_cong': tol_even, 'odd_it_cong': tol_odd}
        return critical_bosonic_levels, diags
    return critical_bosonic_levels


def fscore_crit_bosons(ander_out:str, par:str, qno=[0,0]):
    '''Calculates the iteration at which most levels become flat and returns the levels at that iteration.
    args:
        ander_out [str]: ander.out file
        par [str]: parity of the levels to be considered ['even', 'odd', 'all']
        qno [list]: family of quantum numbers to be considered
    returns:
        ediff_frame: dataframe with the optimized ediff values for each level'''
    assert os.path.isfile(ander_out), f'{ander_out} does not exist'
    levels = aextr(ander_out, 3.0, par).query(f'sf == {qno[0]} and jf == {qno[1]}')
    unique_qnums = levels.drop_duplicates(subset=['sf', 'jf', 'index'])[['sf', 'jf', 'index']]
    ediffs = {'n': levels['n'].unique()[:-1]}
    for (sf, jf, index) in unique_qnums.iloc:
        level = levels.query(f'sf == {sf} and jf == {jf} and index == {index}')
        energy = level['energy'].astype(float)
        if len(energy) > 3:
            if not np.all(energy == 0): #excluding the ground state energy
                ediff = np.abs(pdiff(energy[1:], energy[:-1]))
                if len(ediff) == len(ediffs['n']):
                    ediffs[(sf, jf, index)] = ediff
    ediff_frame =  pd.DataFrame(ediffs)
    minima_locations = ediff_frame.idxmin().to_numpy()
    min_rows, counts = np.unique(ediff_frame.idxmin().to_numpy(), return_counts= True)
    selected_row = min_rows[np.argmax(counts)]
    iteration = ediff_frame.iloc[selected_row].to_numpy()[0]
    return_levels = levels.query(f'n == {iteration}')
    #extremal values: 
    return return_levels