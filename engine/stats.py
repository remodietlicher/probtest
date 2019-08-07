import re
import os
from netCDF4 import Dataset
import numpy as np
import pandas as pd

from util.file_system import file_names_from_regex
from util.constants import dataframe_type_dict


def stats(config):
    file_regex = config.get("file_regex")
    input_dir_regex = config.get("input_dir_regex")
    data_base_dir = config.get("data_base_dir")
    variable_names = config.get("variable_names").split(",")
    time_dim = config.get("time_dim")
    height_dim = config.get("height_dim")
    hor_dims = config.get("hor_dims").split(",")
    out_file_name = config.get("out_file_name")

    input_dirs = ["{}/{}".format(data_base_dir, d) for d in file_names_from_regex(data_base_dir, input_dir_regex)]
    for input_dir in input_dirs:
        # load all model output data files matching the regex
        input_files = file_names_from_regex(input_dir, file_regex)
        data = [Dataset("{}/{}".format(input_dir, f), 'r') for f in input_files]

        frame = {key: np.array([], dtype=dtype) for key, dtype in dataframe_type_dict.items()}

        for d in data:
            time = d.variables[time_dim][:]
            heigth = d.variables[height_dim][:]

            for v in variable_names:
                dims = d.variables[v].dimensions
                var = d.variables[v][:]

                avg_ax = tuple([i for i, dim in enumerate(dims) if dim in hor_dims])
                mean = np.mean(var, axis=avg_ax)
                amax = np.amax(var, axis=avg_ax)
                amin = np.amin(var, axis=avg_ax)

                if height_dim in dims:
                    # TODO: remove assumption that it is always (time_dim, height_dim)
                    v_time = np.repeat(time[:, np.newaxis], len(heigth), axis=1)
                    v_heigth = heigth
                else:
                    # only surface value
                    v_heigth = np.array([-1])
                    v_time = time

                if time_dim in dims:
                    # TODO: remove assumption that it is always (time_dim, height_dim)
                    v_heigth = np.repeat(v_heigth[np.newaxis, :], len(time), axis=0)

                nrows = mean.size

                frame["min"] = np.append(frame["min"], amin.flatten())
                frame["max"] = np.append(frame["max"], amax.flatten())
                frame["mean"] = np.append(frame["mean"], mean.flatten())
                frame["time"] = np.append(frame["time"], v_time.flatten())
                frame["ntime"] = np.append(frame["ntime"], np.zeros(nrows))
                frame["heigth"] = np.append(frame["heigth"], v_heigth.flatten())
                frame["name"] = np.append(frame["name"], [v] * nrows)

        df = pd.DataFrame(frame)

        # sort the data by time
        df.sort_values(by=["time", "heigth"], inplace=True)

        # add column with number of timestep (hacky hacky)
        # TODO make this part pythonic
        timesteps = np.unique(df["time"])
        time = df["time"]
        ntime = np.ones_like(time)
        cnt = 0
        for dt in timesteps:
            ntime[time == dt] = cnt
            cnt += 1
        df["ntime"] = ntime

        out_path = "{}/{}".format(input_dir, out_file_name)
        print("writing stats file to {}.".format(out_path))
        df.to_csv(path_or_buf=out_path, sep=",", index=False)
