import numpy as np
from .aextr import aextr
from .misc_funcs import pdiff
from .extract_crit_bosons import fscore_crit_bosons



def clean_inst(ander_out, s):
    spectrum = aextr(ander_out, 3.0, 'all')
    condition = (spectrum['sf']==0) & (spectrum['jf']==0) & (spectrum['index']==1)
    level = spectrum[condition]
    #find the first iteration where we reach free bosonic energies:
    e_b = free_boson_energy(s) #free bosonic energy
    N = level['n'].to_numpy(dtype=np.float64)
    E = level['energy'].to_numpy(dtype=np.float64)
    free_boson_match = np.min([pdiff(e, e_b) for e in E])
    loc_match = pdiff(0, np.min(E))
    tol = 0.5
    nb = 4
    n_max = 0
    #First check for matching with free bosonic energies
    if free_boson_match < tol: #the first bosonic excitation is close to a free bosonic energy at iteration n_max                            #most probably the delocalized fixed point
        i = np.argmin([pdiff(e, e_b) for e in E])
        n_max = N[i]
        flat_check = 0.5*( pdiff(E[i+1], E[i]) + pdiff(E[i-1], E[i]) )
        if flat_check < 1: #
            stable_fixed_point = spectrum[spectrum['n'] == n_max]
            #check if first nb levels can be described by integer multiple of free bosonic energies
            E_stable = stable_fixed_point['energy'].to_numpy(dtype=np.float64)
            diff = [pdiff(e, i*e_b) for i, e in enumerate(E_stable[:nb])]
            max_diff = max(diff)
            if max_diff<0.5: #stable fixed point is made of only free bosonic energies
                # string = f'{max_diff}, found delocalized fixed point'
                string = 'good'
                # return level[level['n'] <= n_max]
            else:
                string = f'it={n_max},worst_ex_match= {max_diff}, excited states not free'
        else: #unable to decide
            string = f'it={n_max},worst_ex_match= {flat_check}, Unable'
    #Check if it is localized fixed point:
    elif loc_match < tol: #bosonic level reached near degeneracy with ground state at iteration n_max
            i = np.argmin(E)
            n_max = N[i]
            stable_fixed_point = spectrum[spectrum['n'] == n_max]
            E_stable = stable_fixed_point['energy'].to_numpy(dtype=np.float64)
            #check if first few energy levels are doubly degenerate:
            degeneracy = [len(np.where((np.abs(E_stable - e)<tol))[0]) for e in E_stable[:2*nb+1]]
            degen_tol = [np.min(np.nonzero(np.abs(E_stable - e))) for e in E_stable[:2*nb+1]]
            if np.all(np.array(degeneracy) == 2): #degenerate levels in the spectrum
                string = f'it={n_max}, found localized fixed point'
            else:
                string = f'it={n_max}, excited states with degeneracy!=2, {degeneracy}, {degen_tol}'

    else:
        string=f'unable to decide, deloc_match={free_boson_match}, loc_match={loc_match}, {np.min(E)}'
    return n_max, string


def free_boson_energy(s:float):
    '''returns the free bosonic energy for a given band exponent s'''
    free_boson = {0.5: 0.35686718, 0.55: 0.36186088, 0.6: 0.36664897, 0.65: 0.37124349, 0.7: 0.37565565, 0.75: 0.37989588, 0.8: 0.3839739, 0.85: 0.38789876, 0.9: 0.39167889, 0.95: 0.39532217}
    return free_boson[s]


def ph_sym_spect(s, nb, K):
    '''
    Obtain the critical energies (<3.0) of the p-h-symmetric spectrum for l-BFA model with U=0.5, g=5
    args:
        s [float]: bosonic bath exponent
        K [int]: number of states kept
        nb [int]: number of bosons per Wilson site
    returns:
        energies [DataFrame]: energies of the p-h-symmetric spectrum
    '''
    data_base = f'/blue/physics-dept/an.kandala/Localf_model/Boundary_databases/p_h_symmetry'
    ander_out = f'{data_base}/s={s}_K={K}_nb={nb}/last_runs/max.out'
    par = 'all'; phsym = True
    frame = fscore_crit_bosons(ander_out, 'all', [0,0])
    return frame
    

def LC_spect(s, nb):
    '''Obtains the level crossing spectrum for the single impurity model.
    args:
        s [float]: bosonic bath exponent
        nb [int]: number of bosons per Wilson site
    returns:
        LC_spec [DataFrame]: energies of the level crossing spectrum
    '''
    data_base = '/blue/physics-dept/an.kandala/Level_crossing/automated_s/Determining_ediff/runs_data_base'
    path = f'{data_base}/s={s}/nb={nb}/find_edc_runs'
    sub_dirs = [int(d.split('=')[1]) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    sub_dirs.sort()
    g = sub_dirs[-1]
    ander_out = f'{path}/g={g}/last_runs/max.out'
    frame = fscore_crit_bosons(ander_out, 'all', qno=[1,0])
    return frame