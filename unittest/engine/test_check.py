import unittest
import pandas as pd
import numpy as np

from engine.tolerance import compute_max_rel_diff_dataframe
from engine.check import check_variable

TEST_VARIABLES = ["v1", "v2"]
TEST_TIMESTEPS = np.arange(3)


def hand_written_dataframes():
    frame = {}
    frame["ref"] = {"max": [10, 4, 2, 47, 23, 24],
                    "min": [3, 9, 1, 23, 32, 53],
                    "mean": [5, 1, 8, 20, 32, 62],
                    "ntime": [1, 2, 3, 1, 2, 3],
                    "time": [1, 2, 3, 1, 2, 3],
                    "name": ["v1", "v1", "v1", "v2", "v2", "v2"]}

    frame["ref0"] = {"max": [0, 0, 0, 0, 0, 0],
                     "min": [0, 0, 0, 0, 0, 0],
                     "mean": [0, 0, 0, 0, 0, 0],
                     "ntime": [1, 2, 3, 1, 2, 3],
                     "time": [1, 2, 3, 1, 2, 3],
                     "name": ["v1", "v1", "v1", "v2", "v2", "v2"]}

    frame["cur"] = {"max": [1, 2, 5, 79, 93, 34],
                    "min": [3, 3, 5, 78, 13, 64],
                    "mean": [1, 10, 5, 55, 32, 27],
                    "ntime": [1, 2, 3, 1, 2, 3],
                    "time": [1, 2, 3, 1, 2, 3],
                    "name": ["v1", "v1", "v1", "v2", "v2", "v2"]}

    frame["cur0"] = {"max": [0, 0, 0, 0, 0, 0],
                     "min": [0, 0, 0, 0, 0, 0],
                     "mean": [0, 0, 0, 0, 0, 0],
                     "ntime": [1, 2, 3, 1, 2, 3],
                     "time": [1, 2, 3, 1, 2, 3],
                     "name": ["v1", "v1", "v1", "v2", "v2", "v2"]}

    frame["tol1"] = {"max": [10, 10, 10, 100, 100, 100],
                     "min": [10, 10, 10, 100, 100, 100],
                     "mean": [10, 10, 10, 100, 100, 100],
                     "ntime": [1, 2, 3, 1, 2, 3],
                     "time": [1, 2, 3, 1, 2, 3],
                     "name": ["v1", "v1", "v1", "v2", "v2", "v2"]}

    frame["tol2"] = {"max": [4, 4, 4, 40, 40, 40],
                     "min": [4, 4, 4, 40, 40, 40],
                     "mean": [4, 4, 4, 40, 40, 40],
                     "ntime": [1, 2, 3, 1, 2, 3],
                     "time": [1, 2, 3, 1, 2, 3],
                     "name": ["v1", "v1", "v1", "v2", "v2", "v2"]}

    return {key: pd.DataFrame(val).sort_values(by=["name", "ntime"]).reset_index(drop=True)
            for key, val in frame.items()}


class TestCheck(unittest.TestCase):

    def setUp(self):
        self.df_dict = hand_written_dataframes()

    def tearDown(self):
        return

    def test_check(self):
        df_ref = self.df_dict["ref"]
        df_cur = self.df_dict["cur"]
        df_tol1 = self.df_dict["tol1"]
        df_tol2 = self.df_dict["tol2"]

        df_diff = compute_max_rel_diff_dataframe(df_ref, df_cur, TEST_VARIABLES)

        out1, err1, tol1 = check_variable(df_diff, df_tol1)
        out2, err2, tol2 = check_variable(df_diff, df_tol2)
        self.assertTrue(out1, "Check with large tolerances did not validate! Here is the DataFrame:\n{}".format(err1))
        self.assertFalse(out2, "Check with small tolerances did validate! Here is the DataFrame:\n{}".format(err2))

        return

    def test_check_zeros(self):
        df_cur0 = self.df_dict["cur0"]
        df_ref0 = self.df_dict["ref0"]
        df_tol = self.df_dict["tol1"]

        df_diff = compute_max_rel_diff_dataframe(df_ref0, df_cur0, TEST_VARIABLES)

        out1, err1, tol1 = check_variable(df_diff, df_tol)
        self.assertTrue(out1, "Check with large tolerances did not validate! Here is the DataFrame:\n{}".format(err1))


if __name__ == '__main__':
    unittest.main()
