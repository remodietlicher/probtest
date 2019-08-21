import pandas as pd
from util.constants import dataframe_type_dict, compute_statistics, CHECK_THRESHOLD
from util.dataframe_ops import compute_max_rel_diff_dataframe, compute_div_dataframe


def check_variable(diff_df, df_tol):
    diff_tol_df = diff_df.copy()
    for c in diff_df.columns.values:
        if c in compute_statistics:
            diff_tol_df[c] = diff_df[c] - df_tol[c]
        else:
            # we want the real values for 'descriptive' columns
            diff_tol_df[c] = df_tol[c]
        diff_tol_df.loc[diff_tol_df[c].isnull(), c] = 1.0

    # TODO: figure out a way to do this with compute_statistics
    selector = (diff_tol_df["mean"] > CHECK_THRESHOLD) | \
               (diff_tol_df["max"] > CHECK_THRESHOLD) | \
               (diff_tol_df["min"] > CHECK_THRESHOLD)

    return len(diff_tol_df[selector].index) == 0, diff_df[selector], df_tol[selector]


def check(config):
    input_file_ref = config.get("input_file_ref")
    input_file_cur = config.get("input_file_cur")
    tolerance_file_name = config.get("tolerance_file_name")
    check_variable_names = config.get("check_variable_names").split(",")

    df_tol = pd.read_csv(tolerance_file_name, index_col=False, dtype=dataframe_type_dict)
    df_ref = pd.read_csv(input_file_ref, index_col=False, dtype=dataframe_type_dict)
    df_cur = pd.read_csv(input_file_cur, index_col=False, dtype=dataframe_type_dict)

    print("checking {} against {}".format(input_file_cur, input_file_ref))

    diff_df = compute_max_rel_diff_dataframe(df_ref, df_cur, check_variable_names)

    out, err, tol = check_variable(diff_df, df_tol)

    div = compute_div_dataframe(err, tol)

    if out:
        print("RESULT: check PASSED!")
    else:
        print("RESULT: check FAILED")
        print("Differences")
        print(err)
        print("Tolerance")
        print(tol)
        print("Error relative to tolerance")
        print(div)

    return
