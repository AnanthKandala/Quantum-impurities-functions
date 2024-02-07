import matplotlib.pyplot as plt
from matplotlib import rc,rcParams
rc('text', usetex=True)
rc('font', weight='bold')
custom_preamble = {
    "text.latex.preamble":
        r"\usepackage{amsmath,amssymb}" # for the align, center,... environment
        ,
    }
plt.rcParams.update(custom_preamble)

import pandas as pd
from qim_functions import charge
from plot_functions import cont_color
import numpy as np
from pprint import pprint


class counterpower_template:
    def __init__(self, calculation_type:str, chi_frame:pd.DataFrame, num_samples:int):
        self.fig, self.ax = plt.subplots(dpi=300)
        self.ax.set_xlabel(r'$\log T$')
        self.calculation_type = calculation_type
        self.ax.set_ylabel(fr'$\log [T^{{x}}\chi_{calculation_type} ]$')
        self.T = chi_frame['T'].to_numpy()
        self.chi = chi_frame['chi'].to_numpy()
        self.frame = chi_frame
        self.num_samples = num_samples

    def plot(self, power:float, title_misc:str, arg_start:int, n_points:int, file_name:str, t1:float, t2:float, t_plot:list=[]):
        self.plot_all_samples(power, title_misc, t1, t2)
        self.plot_single_sample(arg_start, n_points)
        for t in t_plot:
            self.ax.axvline(np.log10(t), color='k', lw=0.5)
        self.savefig(file_name)
        plt.close(self.fig)
        
    def plot_all_samples(self, power, title_misc, t1, t2):
        self.x = np.log10(self.T)
        self.y = np.log10(self.T**(power)*(self.chi))

        self.ax.plot(self.x, self.y, lw=0.4, ms=3, marker='.', color='k')
        self.ax.set_xlim(t1,t2)
        restricted_chi = self.y[np.where((self.x>t1) & (self.x<t2))]
        y_min = restricted_chi.min()
        y_max = restricted_chi.max()
        if not np.any(np.isnan([y_min, y_max])):
            p = 0.05
            self.ax.set_ylim(y_min - p*(y_max-y_min), y_max + p*(y_max-y_min))
            self.ax.set_title(fr'$\chi_{self.calculation_type}$ vs $T$, $x={power}$, {title_misc}')

    def plot_single_sample(self, arg_start:int, n_points:int):
        num_samples = self.num_samples
        for sample_ind in range(num_samples):
            indices = [n for n in range(len(self.x)) if n%num_samples==sample_ind]
            y_sampled = self.y[indices]
            x_sampled = self.x[indices]
            color = cont_color(sample_ind,num_samples)
            #plotting all the data points in each sample
            self.ax.plot(x_sampled, y_sampled, color=color, lw=0, marker = '.', ms=3)
            #plotting the horizontal line
            y_selected = y_sampled[arg_start: arg_start+n_points] 
            x_selected = x_sampled[arg_start: arg_start+n_points] 
            self.ax.plot(x_selected, y_selected, color=color, lw=0, marker = 'x', ms=4)
            self.ax.axhline(np.mean(y_selected), color=color, lw=0.7)

    def savefig(self, file_name:str):
        self.fig.savefig(file_name)
        plt.close(self.fig)
