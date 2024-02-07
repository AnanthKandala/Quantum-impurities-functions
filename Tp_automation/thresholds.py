def set_thresholds(nb:int):
    '''returns the thresholds for testend5_6 for s=0.6 for nb'''
    thresholds = {"5": [0.3757, 0.8148], "6": [0.5515, 0.6658],
                    "7": [0.4861, 0.6722], "8": [0.4374, 0.6722],
                    "9": [0.3978, 0.6722], "10": [0.385, 0.6722],
                    "11": [0.3783, 0.6722], "12": [0.3763, 0.6722],
                    "13": [0.3758, 0.6722], "14": [0.3757, 0.5853]}
    assert str(nb) in thresholds.keys(), f"nb={nb} not in thresholds.keys()"
    return thresholds[str(nb)]
