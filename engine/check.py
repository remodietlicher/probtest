import pandas as pd
from util.constants import dataframe_type_dict, compute_statistics, CHECK_THRESHOLD
from engine.tolerance import compute_max_rel_diff_dataframe


def check_variable(diff_df, df_tol):
    diff_tol_df = diff_df.copy()
    for c in diff_df.columns.values:
        if c in compute_statistics:
            diff_tol_df[c] = diff_df[c] - df_tol[c]
        else:
            # we want the real values for 'descriptive' columns
            diff_tol_df[c] = df_tol[c]

    # TODO: figure out a way to do this with compute_statistics
    selector = (diff_tol_df["mean"] > CHECK_THRESHOLD) | \
               (diff_tol_df["max"] > CHECK_THRESHOLD) | \
               (diff_tol_df["min"] > CHECK_THRESHOLD)

    return len(diff_tol_df[selector].index) == 0, diff_tol_df[selector]


def check(config):
    input_file_ref = config.get("input_file_ref")
    input_file_cur = config.get("input_file_cur")
    model_output_dir = config.get("model_output_dir")
    tolerance_file_name = config.get("tolerance_file_name")
    check_variable_names = config.get("check_variable_names").split(",")

    tf_path = "{}/{}".format(model_output_dir, tolerance_file_name)

    df_tol = pd.read_csv(tf_path, index_col=False, dtype=dataframe_type_dict)
    df_ref = pd.read_csv(input_file_ref, index_col=False, dtype=dataframe_type_dict)
    df_cur = pd.read_csv(input_file_cur, index_col=False, dtype=dataframe_type_dict)

    print("checking {} against {}".format(input_file_ref, input_file_cur))

    diff_df = compute_max_rel_diff_dataframe(df_ref, df_cur, check_variable_names)

    out, err = check_variable(diff_df, df_tol)

    if out:
        print("check PASSED!")
    else:
        print("check FAILED")
        print(err)

    return
