import pandas as pd
import numpy as np
import itertools

from util.file_system import file_names_from_regex
from util.constants import dataframe_type_dict


def tolerance(config):
    data_base_dir = config.get("data_base_dir")
    perturb_dir_regex = config.get("perturb_dir_regex")
    input_file_name = config.get("input_file_name")
    tolerance_file = config.get("tolerance_file")
    variable_names = config.get("variable_names").split(",")

    perturb_dirs = file_names_from_regex(data_base_dir, perturb_dir_regex)

    # TODO: can the dtype be specified per column?
    dfs = [pd.read_csv("{}/{}/{}".format(data_base_dir, d, input_file_name),
                       sep=",", dtype=dataframe_type_dict, index_col=False)
           for d in perturb_dirs]

    compute_diff = ["mean", "max", "min"]
    diff_df = pd.concat([((dfs[0][c] - dfs[1][c]) / dfs[0][c]).abs() for c in compute_diff], axis=1)

    # we want the real values for 'descriptive' columns
    diff_df["heigth"] = dfs[0]["heigth"]
    diff_df["time"] = dfs[0]["time"]
    diff_df["ntime"] = dfs[0]["ntime"]
    diff_df["name"] = dfs[0]["name"]

    # get timesteps in dataframe
    timesteps = np.unique(diff_df["ntime"])
    time_var = list(itertools.product(timesteps, variable_names))

    selector = [(diff_df["ntime"] == t) & (diff_df["name"] == n) for t, n in time_var]

    # construct new dataframe with max values for each timestep
    dt_max = pd.concat([diff_df[s].max() for s in selector], axis=1).T

    # sort dataframe by name
    dt_max.sort_values(by=["name", "ntime"], inplace=True)

    print("writing tolerance file to {}.".format(tolerance_file))
    dt_max.to_csv(tolerance_file, index=False)

    return
