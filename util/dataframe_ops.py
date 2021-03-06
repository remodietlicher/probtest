import numpy as np
import itertools
import pandas as pd

from util.constants import compute_statistics

pd.set_option('display.max_colwidth', -1)
pd.set_option('display.max_columns', None)


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
    # NOTE: at this point, the information about the levels is lost as min, max and mean can have largest differences on
    #       different levels
    df_max = pd.concat([diff_df[s].max() for s in selector], axis=1).T

    # sort dataframe by name
    df_max.sort_values(by=["name", "ntime"], inplace=True)
    df_max.reset_index(inplace=True, drop=True)

    return df_max


def compute_div_dataframe(df1, df2):
    out = df1.copy()
    for c in df1.columns.values:
        if c in compute_statistics:
            out[c] = df1[c] / df2[c].replace({0: np.nan})
        else:
            out[c] = df1[c]
    return out


def pretty_print(df):
    fmt = {c: '{:.4e}'.format for c in compute_statistics}
    fmt['ntime'] = '{:d}'.format

    print(df.drop("time", axis=1).replace({np.nan: 0}).to_string(formatters=fmt, index=False))


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
