import re
import pandas as pd
import numpy as np
import os

####################################################################################################################################
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
    #Obtain all the levels from the file at each iteration
    


def get_flat_bosonic_levels(data_frame, return_tol=False):
    '''
    Returns the bosonic levels at the flattest iteration. Flattest iteration decided using the lowest bosonic excitation.
    **args: data_frame: pandas dataframe with all the levels
    **returns: pandas dataframe with the bosonic levels at the flattest iteration
           and the tolerance of the lowest bosonic excitation energy and the iteration at which it occurs.
    '''
    


def get_critical_bosons(ander_file, par, phsym, return_tol=False):
    '''
    Returns the critcal bosonic levels at the flattest iteration. Flattest iteration decided using the lowest bosonic excitation.
    for the BFA model, it checks if the spectrum decomposes into ferimions times bosons. Critical bosons should appear in odd and even iterations.
    **args: data_frame: pandas dataframe with all the levels, par: 'even' for models with fermions and 'all' for the models without fermions.
    **returns: pandas dataframe with the bosonic levels at the (even) flattest iteration.
         if return_tol=True, it also returns the flatness tolerance at even and odd iterations.
    '''
    

def extract_level(infile, qno, par):
    '''
    extracts the level with qno=[sf,jf,index] from the output file as a function of iteration number.
    **arge: infile, qno=[sf,jf,index], par='even' for models with fermions and 'all' for the models without fermions.
    '''
   

def extract_it(infile, it):
    '''
    extracts the levels at iteration number it from the output file.
    **arge: infile, it
    '''
   


def charge(ander_out):
    '''Extracts <n_d> as a function of temperature from the ander.out file.
       args: location of the ander.out file
        returns: pandas dataframe with columns 'T' and 'nd'
    '''
    


def spin(ander_out, h):
    '''Extracts Chi_s vs T as a function of temperature from the ander.out file.
       args: location of the ander.out file, h ---> magnetic field
        returns: pandas dataframe with columns 'T' and 'chi'
    '''
    

###############################################################################################################################################
#Functions to process the ander.in file
def ander_in(infile, driver):
    '''
    Extracts the parameters from the ander.in file and returns them as a dictionary.
    parameters = {
            'ed': ed,
            'U': U,
            'eta': eta,
            'Gamma': Gamma,
            'delta': delta,
            'g': g,
            'K': K,
            'lower_threshold': lower_threshold,
            'upper_threshold': upper_threshold,
        }
    '''
    


def cdw(infile):
    #convert windows directory to linux directory
    return re.sub('\\\\', '/', infile)


###############################################################################################################################################
#Functions to process ander.log file
def log_couplings(infile):
    '''
    extract the values closest to the critical point from ander.log file.
    returns the lower and upper bounds on the critical coupling: [gmin, gmax]
    '''
    f = open(infile, "r")
    A = f.readlines()
    gg = A[-2].split()
    gmin = float(gg[0])
    gmax = float(gg[1])
    return [gmin, gmax]


def extract_t_star(infile):
    '''
    extracts the variation of T* w.r.t fractional distance for the critical point
    returns two dictionaries: T = {1:[], 2:[]}, G = {1:[], 2:[]} 
    T contains the T* for each phase. G contains abs(-1 + g/gc) for each phase'''
    

def max_n(infile):
    '''
    extracts the maximum number of iterations from the ander.log file
    args: location of the log file
    returns: n_max for min and max phases
    '''
    


####misc
def create(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    return


def clean(T, y):
    '''
    removes the rows with nan values from the dataframe
    '''
   