import numpy as np

MODE_PERTURB = 'perturb'
MODE_CHECK = 'check'
MODE_STATS = 'stats'
MODE_TOLERANCE = 'tolerance'
MODE_RUN_ENSEMBLE = 'run'
MODE_VISUALIZE = 'visualize'
CHECK_THRESHOLD = 1e-15

dataframe_type_dict = {"min": np.float64, "mean": np.float64, "max": np.float64, "ntime": np.int32,
                       "time": np.float64, "height": np.float64, "name": str}

compute_statistics = ["max", "min", "mean"]

exp_modifier = "_seed_{seed}"
perturbed_model_input_subdir = "perturbed_input"
