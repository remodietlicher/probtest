import pandas as pd
import itertools
import sys

from util.constants import dataframe_type_dict, compute_statistics, exp_modifier
from util.dataframe_ops import compute_max_rel_diff_dataframe, select_max_diff


def tolerance(config):
    stats_file_name = config.get("stats_file_name")
    tolerance_file_name = config.get("tolerance_file_name")
    model_output_dir = config.get("model_output_dir")
    experiment_name = config.get("experiment_name")
    check_variable_names = config.get("check_variable_names").split(",")
    seeds = config.get("seeds").split(",")
    factor = config.getint("factor")

    # exp_modifier has a {seed} variable to be set
    stats_file_path = '{}/{}/{}'.format(model_output_dir, experiment_name + exp_modifier, stats_file_name)

    # read in stats files
    dfs = [pd.read_csv(stats_file_path.format(seed=s), sep=",", dtype=dataframe_type_dict, index_col=False)
           for s in seeds]

    ndata = len(dfs)
    if ndata < 2:
        print("not enough data to compute tolerance, got {} dataset. Abort.".format(ndata))
        sys.exit(1)
    # get all possible combinations of the input data
    combs = list(itertools.product(range(ndata), range(ndata)))

    # do not use the i==j combinations
    combs = [(i, j) for i, j in combs if i != j]
    print("computing tolerance from {} input combinations!".format(len(combs)))
    dfs_max = [compute_max_rel_diff_dataframe(dfs[i], dfs[j], check_variable_names) for i, j in combs]

    df_max = select_max_diff(dfs_max, check_variable_names)

    print("applying a factor of {} to the spread".format(factor))
    df_max[compute_statistics] = df_max[compute_statistics] * factor

    print("writing tolerance file to {}.".format(tolerance_file_name))
    df_max.to_csv(tolerance_file_name, index=False)

    return
