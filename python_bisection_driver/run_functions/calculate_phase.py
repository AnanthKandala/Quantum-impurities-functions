import pandas as pd
import numpy as np
from qim_functions import aextr, free_boson_energy, pdiff



def check_degeneracy(it, spectrum, degen_tol=1e-2):
    '''Check if there are levels that are close to each other'''
    levels = spectrum.query(f'n == {int(it)}')['energy'].to_numpy(float)
    diff = np.diff(levels)
    if np.any(diff < degen_tol):
        degen_score = 100
    else:
        degen_score = 0
    return degen_score

def calculate_phase(s, ander_out, phase_tol):
    emax = 3.0
    spectrum = aextr(ander_out, emax, 'all')
    free_bosons = np.array([i*free_boson_energy(s) for i in range(6)])
    n_levels = len(free_bosons)
    iterations = np.unique(spectrum['n'].to_numpy())
    error = np.empty(len(iterations))
    for i, n in enumerate(iterations):
        energies = spectrum.query(f'n=={n}')['energy'].to_numpy()[:n_levels]
        error[i] = np.average(np.abs(pdiff(energies, free_bosons))) + check_degeneracy(n, spectrum)
        
    if np.min(error) < phase_tol:
        phase = 'delocalized'
    else:
        phase = 'localized'
    return phase


