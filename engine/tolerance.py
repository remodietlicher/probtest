import pandas as pd
import numpy as np
import itertools

from util.constants import dataframe_type_dict, compute_statistics


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


def tolerance(config):
    model_output_dir = config.get("model_output_dir")
    perturbed_model_output_dir = config.get("perturbed_model_output_dir")
    stats_file_name = config.get("stats_file_name")
    tolerance_file_name = config.get("tolerance_file_name")
    check_variable_names = config.get("check_variable_names").split(",")
    seeds = config.get("seeds").split(",")
    factor = config.getint("factor")

    # look for directories with the model perturbed model input dir prefix
    perturb_dirs = [perturbed_model_output_dir.format(s) for s in seeds]

    # read in stats files
    dfs = [pd.read_csv("{}/{}/{}".format(model_output_dir, d, stats_file_name),
                       sep=",", dtype=dataframe_type_dict, index_col=False)
           for d in perturb_dirs]

    ndata = len(dfs)
    # get all possible combinations of the input data
    combs = list(itertools.product(range(ndata), range(ndata)))

    # do not use the i==j combinations
    combs = [(i, j) for i, j in combs if i != j]
    print("computing tolerance from {} input combinations!".format(len(combs)))
    dfs_max = [compute_max_rel_diff_dataframe(dfs[i], dfs[j], check_variable_names) for i, j in combs]

    df_max = select_max_diff(dfs_max, check_variable_names)

    print("applying a factor of {} to the spread".format(factor))
    df_max[compute_statistics] = df_max[compute_statistics] * factor

    path = "{}/{}".format(model_output_dir, tolerance_file_name)
    print("writing tolerance file to {}.".format(path))
    df_max.to_csv(path, index=False)

    return
