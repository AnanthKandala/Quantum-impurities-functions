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


#Version that uses np.unique to identify the levels.
def lev_opt(levels_df, outimage, title, B_crit, plot_type): #plot_type = 'relative' or 'absolute' will determine if the levels are plotted w.r.t the ground state or not.
    
    fig, ax = plt.subplots(dpi=300)
    #setting figure parameters.
    ax.set_title(title)
    ax.set_ylabel('E')
    ax.set_xlabel('N')
    emax = 3.0
    ax.set_ylim(0.0,emax)
    n1 = 0 #int(np.min(A[:,0]))
    n2 = 28 #int(np.max(A[:,0]))
    ms = 3
    x_ticks = range(n1,n2+2,2)
    ax.set_xticks(x_ticks)
    x_ticks = np.arange(n1,n2+4,4)
    ax.set_xlim(n1, n2)
    
    #plotting legend
    marker = {-1:'o', 0:'s', 1:'x', 2:'.', -2:'.', 'none':'.'} #jf_values -> marker for the level
    name = {-1:'P', 0:'B', 1:'H',2:'D', -2:'D'} #jf_values -> label in the legend
    color = {-1:'blue', 0:'red', 1: 'green', 2:'yellow',-2:'yellow', 'none':'k'} #jf_value -> color of the level
    

    #plotting free bosonic energies
    eb = 0.36664911
    e1 = eb
    while e1<=emax:
        ax.axhline(e1,linewidth=0.7,linestyle='dashed',color='b')
        e1+=eb
    # X = np.linspace(0, 100, 30)
    for e in B_crit:
        ax.axhline(e,linewidth=0.7,color='k')

    # E_loc=np.array([0. , 0.49276093, 1.09327376, 1.80579008])+0.1853
    # for e in E_loc:
    #     ax.axhline(e,color='b',linestyle='dotted',linewidth=0.7)
        # 0  1   2   3   4
    A = np.array(levels_df[['iteration', 'energy', 'sf', 'jf', 'occurance']]).astype(float)
    #A = [N, E, sf, jf, ind]

    
    #plotting the crititical energies in one go
    E_crit = []
    N_crit = []
    def flat(N, E):
        ind = np.argmin(np.abs(E[1:]-E[:-1]))
        return N[ind], E[ind]
    #Unique levels:
    unique_qno = np.unique(A[:,[2,3,4]], axis=0)
    plotted_jf = []
    for qno in unique_qno:
        indices = np.where(np.all(A[:,[2,3,4]] == qno , axis = 1))[0]
        N = A[indices, 0]
        E = A[indices, 1]
        ax.plot(N, E, ls='solid', linewidth=0.4, color='k')
        level_type = int(qno[1])
        ax.plot(N, E, color=color[level_type], markersize=ms, marker=marker[level_type], lw=0, alpha=0.5) 
        if level_type not in plotted_jf:
            plotted_jf.append(level_type)


    for key in name.keys():
    # ax.plot([n], [A[k, 1]], color=color[level_type], markersize=ms, marker=marker[level_type])
        if key in plotted_jf:            
            ax.plot([], [], lw=0,color=color[key], markersize=ms, marker=marker[key], label=fr'${key}$')
              
    #plotting the thresholds used in the find_driver
    # for e in [0.159, 0.162 ]:
    #     ax.axhline(e, lw=0.5, color='k')
    ax.legend(loc=0, fontsize='x-small', title='$j_f$')
    fig.savefig(outimage)
    plt.close(fig)
    return 



        
        # if np.all(qno == [0, 1]):
        #     ax.plot(N, E, ls='solid', linewidth=0.5, color='r', zorder=1000)
        #obtaining the ground-state:
    # ground_state_indices = np.where((A[:,1]==0) & (A[:,-1]==0))[0]
    # ground_state_qno = {}
    # for n,jf in A[ground_state_indices][:,[0,3]]:
    #     ground_state_qno[int(n)] = jf
        
        #identifying the 'flattest' energies:
#         E_select = E[np.where(E<emax)]
#         N_select = N[np.where(E<emax)]
        
#         if len(E_select) > 2 and np.any(E_select<emax):
#             n_min ,e_crit = flat(N_select, E_select)
#             ax.axhline(e_crit, lw=0.2, color='r')
#             ax.axvline(n_min, lw=0.2, color='r')
#             E_crit.append(e_crit)
#             N_crit.append(n_min)
#         ax.scatter(N_crit, E_crit, marker='o', facecolors='none', edgecolors='black'  )
#         jf = qno[1]
#         # print(N)

#         L_type = np.empty(len(E_select))
#         for k, e in enumerate(E_select):
#             n = int(N_select[k])  
#             e = float(e)
#             # print(A[k,:], n, jf, ground_state_qno[int(n)])
            
#             if e!=0 and plot_type == 'relative': #plotting excited-states w.r.t the ground state.
#                     level_type = int(jf-ground_state_qno[int(n)]) 
#             else:
#                 level_type = int(jf)

#             if level_type in color.keys():
#                 L_type[k] = level_type
#                 # markers.append(marker[level_type])
#                 # colors.append(color[level_type])
#                     # ax.plot([n], [e], color=color[level_type], markersize=ms, marker=marker[level_type])    
#             else:
#                 L_type[k] = 'none'
#                 print(f'none had been found, {e} {n} {jf}')

#         for level_type in np.unique(L_type):
#             mask = np.where(L_type==level_type)
#             ax.plot(N[mask], E[mask], color=color[level_type], markersize=ms, marker=marker[level_type], lw=0, alpha=0.5) 
#             if level_type not in plotted_jf:
#                 plotted_jf.append(level_type)