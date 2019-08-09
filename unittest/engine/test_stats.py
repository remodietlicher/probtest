import unittest
from netCDF4 import Dataset
import numpy as np
import os

from engine.stats import create_stats_dataframe
from util.constants import compute_statistics

DUMMY_FILE_NAME = "test_stats.nc"

TIME_DIM_SIZE = 10
Z_DIM_SIZE = 50
X_DIM_SIZE = 100
Y_DIM_SIZE = 100


def initialize_dummy_netcdf_file(name):
    data = Dataset(name, "w")

    data.createDimension("t", size=TIME_DIM_SIZE)
    data.createVariable("t", np.float64, dimensions="t")
    data.variables["t"][:] = np.arange(TIME_DIM_SIZE)

    data.createDimension("x", size=X_DIM_SIZE)
    data.createVariable("x", np.float64, dimensions="x")
    data.variables["x"][:] = np.arange(X_DIM_SIZE)

    data.createDimension("y", size=Y_DIM_SIZE)
    data.createVariable("y", np.float64, dimensions="y")
    data.variables["y"][:] = np.arange(Y_DIM_SIZE)

    data.createDimension("z", size=Z_DIM_SIZE)
    data.createVariable("z", np.float64, dimensions="z")
    data.variables["z"][:] = np.arange(Z_DIM_SIZE)

    return data


class TestStats(unittest.TestCase):

    def setUp(self):
        self.data = initialize_dummy_netcdf_file(DUMMY_FILE_NAME)

        self.data.createVariable("v1", np.float64, dimensions=("t", "x", "y", "z"))
        self.data.variables["v1"][:] = np.ones((TIME_DIM_SIZE, X_DIM_SIZE, Y_DIM_SIZE, Z_DIM_SIZE))
        self.data.variables["v1"][:, :, 0, :] = self.data.variables["v1"][:, :, 0, :] - 1
        self.data.variables["v1"][:, :, -1, :] = self.data.variables["v1"][:, :, -1, :] + 1

        self.data.createVariable("v2", np.float64, dimensions=("t", "x", "z"))
        self.data.variables["v2"][:] = np.ones((TIME_DIM_SIZE, X_DIM_SIZE, Z_DIM_SIZE)) * 2
        self.data.variables["v2"][:, 0, :] = self.data.variables["v2"][:, 0, :] - 1
        self.data.variables["v2"][:, -1, :] = self.data.variables["v2"][:, -1, :] + 1

        self.data.createVariable("v3", np.float64, dimensions=("t", "x"))
        self.data.variables["v3"][:] = np.ones((TIME_DIM_SIZE, X_DIM_SIZE)) * 3
        self.data.variables["v3"][:, 0] = self.data.variables["v3"][:, 0] - 1
        self.data.variables["v3"][:, -1] = self.data.variables["v3"][:, -1] + 1

    def TearDown(self):
        self.data.close()
        os.remove(DUMMY_FILE_NAME)

    def test_stats(self):

        var_names = ["v1", "v2", "v3"]
        time_dim = "t"
        height_dim = "z"
        hor_dims = ["x", "y"]

        df = create_stats_dataframe([self.data], var_names, time_dim, height_dim, hor_dims)

        # check that the "time" and "ntime" columns are the same (for time given as arange)
        time_check_arr = df["ntime"] - df["time"]
        time_check = np.sum(time_check_arr)
        self.assertEqual(time_check, 0)

        # check that the min/mean/max are correct
        ref_dict = {"min": [0, 1, 2], "mean": [1, 2, 3], "max": [2, 3, 4]}
        for i, vn in enumerate(var_names):
            for c in compute_statistics:
                unique = np.unique(df[df["name"] == vn][c])
                self.assertEqual(len(unique), 1, "too many values in statistics for dataframe")
                unique = unique[0]
                self.assertEqual(unique, ref_dict[c][i],
                                 "values are incorrect for variable {} and statistic {}".format(vn, c))


if __name__ == '__main__':
    unittest.main()
