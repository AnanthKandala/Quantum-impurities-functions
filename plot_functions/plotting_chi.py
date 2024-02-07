import pandas as pd
import numpy as np
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



def plot_counter(chi_data, var, inputs, t_plot, t_fit):
    ''''plots chi_{var} vs T with a counter power of power'''
    (c,power, n_points, arg_start) = inputs
    power = round(power, 8)
    fig, ax = plt.subplots(nrows=1,ncols=1)
    T = chi_data['T']
    chi = chi_data['chi']
    x = np.log10(T)
    y = np.log10(T**(power)*(chi))
    ax.plot(x,y, lw=0.4, ms=3, marker='.', color='k')
    ax.set_title(fr'K=200, critical endpoint local $\chi_c$, $x={power}$')
    ax.set_ylabel(fr'$\log(T^{x}\chi_{var})$')
    ax.set_xlabel(r'$\log(T)$')  
    (t1, t2) =t_plot
    t2=-1
    xmin=-15.0
    xmax=-6.0
    indices = np.where((x>=xmin) & (x<=xmax))[0]
    ymin = np.min(y[indices])
    ymax = np.max(y[indices])
    ax.set_xlim(t1,t2)
    p = 0.1
    ax.set_ylim(ymin - p*(ymax-ymin),ymax + p*(ymax-ymin))

    #split into different samples and draw a horinzontal line through the mean
    n_max = 10
    for sample_ind in range(n_max):
        indices = [n for n in range(len(x)) if n%n_max==sample_ind]
        y_sampled = y[indices]
        x_sampled = x[indices]
        color = plt.cm.tab20.colors[sample_ind]
        # color = 'b'
        #plotting all the data points in each sample
        ax.plot(x_sampled, y_sampled, color=color, lw=0.5, marker = '.', ms=3)
        #plotting the horizontal line
        y_selected = y_sampled[arg_start: arg_start+n_points] 
        x_selected = x_sampled[arg_start: arg_start+n_points] 
        ax.plot(x_selected, y_selected, color=color, lw=0, marker = 'x', ms=4)
        ax.axhline(np.mean(y_selected), color=color, lw=0.7)
    
    fig.savefig(f'{path_0}/counter_power/{c}_{power}.jpeg',dpi=500)
    plt.close(fig)
    return