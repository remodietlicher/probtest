import numpy as np

MODE_PERTURB = 'perturb'
MODE_CHECK = 'check'
MODE_STATS = 'stats'
MODE_TOLERANCE = 'tolerance'

dataframe_type_dict = {"min": np.float64, "mean": np.float64, "max": np.float64, "ntime": np.int32,
                       "time": np.float64, "heigth": np.float64, "name": str}
