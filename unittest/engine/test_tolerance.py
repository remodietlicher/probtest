import unittest
import pandas as pd
import numpy as np

from engine.tolerance import get_time_var_selector, compute_statistics, select_max_diff, compute_max_rel_diff_dataframe
from util.constants import compute_statistics, dataframe_type_dict

TEST_VARIABLES = ["v1", "v2"]
TEST_TIMESTEPS = np.arange(3)


def create_dummy_tol_dataframe(k):
    frame = {}

    size = len(TEST_VARIABLES) * len(TEST_TIMESTEPS)
    for c in compute_statistics:
        frame[c] = np.ones(size) * k

    frame["ntime"] = np.repeat(TEST_TIMESTEPS, len(TEST_VARIABLES))
    frame["time"] = np.repeat(TEST_TIMESTEPS, len(TEST_VARIABLES))
    frame["name"] = TEST_VARIABLES * len(TEST_TIMESTEPS)

    df = pd.DataFrame.from_dict(frame)

    return df


def hand_written_dataframes():
    frame = [None] * 3
    frame[0] = {"max": [10, 4, 2, 56, 79, 38],
                "min": [3, 9, 1, 97, 46, 52],
                "mean": [5, 1, 8, 16, 24, 94],
                "ntime": [1, 2, 3, 1, 2, 3],
                "time": [1, 2, 3, 1, 2, 3],
                "name": ["v1", "v1", "v1", "v2", "v2", "v2"]}

    frame[1] = {"max": [1, 2, 5, 28, 64, 13],
                "min": [3, 3, 5, 24, 12, 64],
                "mean": [1, 10, 5, 35, 85, 13],
                "ntime": [1, 2, 3, 1, 2, 3],
                "time": [1, 2, 3, 1, 2, 3],
                "name": ["v1", "v1", "v1", "v2", "v2", "v2"]}

    frame[2] = {"max": [1, 4, 2, 79, 89, 64],
                "min": [8, 6, 10, 25, 46, 35],
                "mean": [2, 3, 1, 15, 45, 57],
                "ntime": [1, 2, 3, 1, 2, 3],
                "time": [1, 2, 3, 1, 2, 3],
                "name": ["v1", "v1", "v1", "v2", "v2", "v2"]}

    df_ref = {"max": [10, 4, 5, 79, 89, 64],
              "min": [8, 9, 10, 97, 46, 64],
              "mean": [5, 10, 8, 35, 85, 94],
              "ntime": [1, 2, 3, 1, 2, 3],
              "time": [1, 2, 3, 1, 2, 3],
              "name": ["v1", "v1", "v1", "v2", "v2", "v2"]}

    return [pd.DataFrame(d).sort_values(by=["name", "ntime"]).reset_index(drop=True)
            for d in frame], pd.DataFrame(df_ref)


class TestTolerance(unittest.TestCase):

    def setUp(self):
        self.dfs = [create_dummy_tol_dataframe(k) for k in [1, 10]]
        self.hand_dfs, self.df_ref = hand_written_dataframes()

    def tearDown(self):
        return

    def test_tolerance(self):
        diff = compute_max_rel_diff_dataframe(self.dfs[0], self.dfs[1], TEST_VARIABLES)
        for c in compute_statistics:
            ref = np.ones(len(diff.index))*9
            self.assertTrue((diff[c] == ref).all(), "Compute rel diff failed on statistic {}".format(c))

        df_max = select_max_diff(self.hand_dfs, TEST_VARIABLES)
        for c in compute_statistics:
            self.assertTrue((df_max[c].values == self.df_ref[c].values).all(),
                            "Select max test failed on statistic {}. Got {} instead of {}"
                            .format(c, df_max[c], self.df_ref[c]))

        self.assertTrue((df_max.index == self.df_ref.index).all(), "indices of DataFrames do not match!")


if __name__ == '__main__':
    unittest.main()
