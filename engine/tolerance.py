import pandas as pd
import numpy as np
import itertools

from util.file_system import file_names_from_regex
from util.constants import dataframe_type_dict


def get_time_var_selector(dataframe, check_variable_names):
    # construct product of timesteps and check_variable_names
    timesteps = np.unique(dataframe["ntime"])
    time_var = list(itertools.product(timesteps, check_variable_names))

    # get a selector for each timestep/variable_name combination
    selector = [(dataframe["ntime"] == t) & (dataframe["name"] == n) for t, n in time_var]

    return selector


def compute_max_diff_dataframe(dataframe_ref, dataframe_cur, check_variable_names):
    compute_diff = ["mean", "max", "min"]
    diff_df = pd.concat([((dataframe_ref[c] - dataframe_cur[c]) / dataframe_ref[c]).abs() for c in compute_diff],
                        axis=1)

    # we want the real values for 'descriptive' columns
    diff_df["heigth"] = dataframe_ref["heigth"]
    diff_df["time"] = dataframe_ref["time"]
    diff_df["ntime"] = dataframe_ref["ntime"]
    diff_df["name"] = dataframe_ref["name"]

    selector = get_time_var_selector(diff_df, check_variable_names)

    # construct new dataframe with max differences for each timestep
    df_max = pd.concat([diff_df[s].max() for s in selector], axis=1).T

    # sort dataframe by name
    df_max.sort_values(by=["name", "ntime"], inplace=True)

    return df_max


def select_max_diff(diff_dataframes, check_variable_names):
    # concatenate the dataframes for each perturbed model run
    concat = pd.concat(diff_dataframes, axis=0)

    # get the selector on the concatenated dataframe
    selector = get_time_var_selector(concat, check_variable_names)

    # construct new dataframe with max differences for each timestep over all diff_dataframes
    df_max = pd.concat([concat[s].max() for s in selector], axis=1).T

    # sort the max frame
    df_max.sort_values(by=["name", "time"], inplace=True)

    return df_max


def tolerance(config):
    model_output_dir = config.get("model_output_dir")
    perturbed_model_output_dir = config.get("perturbed_model_output_dir")
    stats_file_name = config.get("stats_file_name")
    tolerance_file_name = config.get("tolerance_file_name")
    check_variable_names = config.get("check_variable_names").split(",")

    # look for directories with the model perturbed model input dir prefix
    perturb_dirs = file_names_from_regex(model_output_dir, perturbed_model_output_dir.format("[0-9]+"))

    # read in stats files
    dfs = [pd.read_csv("{}/{}/{}".format(model_output_dir, d, stats_file_name),
                       sep=",", dtype=dataframe_type_dict, index_col=False)
           for d in perturb_dirs]

    dfs_max = [compute_max_diff_dataframe(dfs[0], dfs[i], check_variable_names) for i in np.arange(1, len(dfs))]

    df_max = select_max_diff(dfs_max, check_variable_names)

    path = "{}/{}".format(model_output_dir, tolerance_file_name)
    print("writing tolerance file to {}.".format(path))
    df_max.to_csv(path, index=False)

    return
