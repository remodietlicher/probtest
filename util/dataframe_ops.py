import numpy as np
import itertools
import pandas as pd

from util.constants import compute_statistics


def get_time_var_selector(dataframe, check_variable_names):
    # construct product of timesteps and check_variable_names
    timesteps = np.unique(dataframe["ntime"])
    time_var = list(itertools.product(timesteps, check_variable_names))

    # get a selector for each timestep/variable_name combination
    selector = [(dataframe["ntime"] == t) & (dataframe["name"] == n) for t, n in time_var]

    return selector


def compute_max_rel_diff_dataframe(dataframe_ref, dataframe_cur, check_variable_names):
    diff_df = dataframe_cur.copy()
    for c in dataframe_ref.columns.values:
        if c in compute_statistics:
            diff_df[c] = ((dataframe_ref[c] - dataframe_cur[c]) / dataframe_ref[c]).abs()
        else:
            # we want the real values for 'descriptive' columns
            diff_df[c] = dataframe_ref[c]

    selector = get_time_var_selector(diff_df, check_variable_names)

    # construct new dataframe with max differences for each timestep
    df_max = pd.concat([diff_df[s].max() for s in selector], axis=1).T

    # sort dataframe by name
    df_max.sort_values(by=["name", "ntime"], inplace=True)
    df_max.reset_index(inplace=True, drop=True)

    return df_max


def select_max_diff(diff_dataframes, check_variable_names):
    # concatenate the dataframes for each perturbed model run
    concat = pd.concat(diff_dataframes, axis=0, ignore_index=True)

    # get the selector on the concatenated dataframe
    selector = get_time_var_selector(concat, check_variable_names)

    # construct new dataframe with max differences for each timestep and statistic over all diff_dataframes
    df_max = pd.concat([concat[s].max() for s in selector], axis=1).T

    # sort the max frame
    df_max.sort_values(by=["name", "time"], inplace=True)
    df_max.reset_index(inplace=True, drop=True)

    return df_max
