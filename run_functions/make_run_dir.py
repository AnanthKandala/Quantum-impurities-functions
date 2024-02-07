import os
from qim_functions import create, symlink

#################################functions to create runs of various kinds############################################


def create_run_dir(path, files:dict, s:float=None, r:float=None, clear_directory=True) -> None:
    '''creates a run directory with the files in files'''
    create(path)
    if clear_directory:
        os.system(f'rm -rf {path}/*')
    ander_path = r'/home/an.kandala/proj/anderson/src/nrg/my_Keep/Hipergator/loginnodes/'
    files['ander'] = os.path.join(ander_path, files['ander']) #ander executable

    ander_data_path = fr'/home/an.kandala/proj/anderson/bin/linux/Keep/login_nodes/'
    files['ander.data'] = os.path.join(ander_data_path, files['ander.data'])


    if s:
        files['ander.bath'] = fr'/home/an.kandala/proj/discretization/1imp/9/s={s}'
    if r:
        files['ander.band'] = fr'/home/an.kandala/proj/discretization/1imp/9/r={r}'
    for file, src in files.items():
        symlink(src, path, file)
    return