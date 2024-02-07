import os


####################################################################
# function that processes the directory that contains find_driver runs. function is called by the gspec.py file.
def process_run_dir(path):
    '''
    obtains the last runs from the ander.log file and copies them to the last_runs folder in the pwd.
    '''
    # Obtaining the phase as a function of the run index
    file = f"{path}/ander.log"
    phase_status = {'1':[False,0], '2':[False,0]}
    max_index = 0
    with open(file, "r") as f:
        for line in reversed(list(f)):
            if '>' in line:
                split_line = line.split()
                phase = split_line[-1].rstrip('\n')
                run_index = split_line[0].split('>')[0]
                if int(run_index) > max_index: #updating the max index
                    max_index = int(run_index)
                if phase in phase_status.keys():
                    if not phase_status[phase][0]:
                        phase_status[phase][0] = True
                        phase_status[phase][1] = run_index  #one of the phases has been found
                if phase_status['1'][0] and phase_status['2'][0]:
                    print('both phases have been found')
                    break #both phases have been found

    #renaming the last output
    if os.path.isfile(f'{path}/ander.out'): #check if there is a file called ander.out in the pwd:
        print('last output renamed')
        os.system(f'mv {path}/ander.out {path}/ander.out{str(max_index).zfill(2)}')

    if phase_status['1'][0] and phase_status['2'][0]: #"Phase 1 and 2 have been found in the log file"
        #copying the last outputs to the last_runs folder
        if not os.path.isdir(f'{path}/last_runs'):
            os.mkdir(f'{path}/last_runs')
        for c, ph in enumerate(['min', 'max']):
            ph_string = phase_status[str(c+1)][1].zfill(2)
            os.system(f'cp {path}/ander.out{ph_string} {path}/last_runs/{ph}.out')
        os.system(f'cp {path}/ander.in {path}/last_runs/.')
        os.system(f'cp {path}/ander.log {path}/last_runs/.')
    else:
        print('both phases not found in the log file')
    return
