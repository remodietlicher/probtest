from netCDF4 import Dataset
import numpy as np
import pandas as pd
import sys

from util.file_system import file_names_from_regex
from util.constants import dataframe_type_dict, perturbed_model_input_subdir, exp_modifier


def create_stats_dataframe(data, check_variable_names, time_dim, height_dim, hor_dims):
    frame = {key: np.array([], dtype=dtype) for key, dtype in dataframe_type_dict.items()}

    for d in data:
        time = d.variables[time_dim][:]
        height = d.variables[height_dim][:]

        for v in check_variable_names:
            dims = d.variables[v].dimensions
            var = d.variables[v][:]

            avg_ax = tuple([i for i, dim in enumerate(dims) if dim in hor_dims])
            mean = np.mean(var, axis=avg_ax)
            amax = np.amax(var, axis=avg_ax)
            amin = np.amin(var, axis=avg_ax)

            if height_dim in dims:
                # TODO: remove assumption that it is always (time_dim, height_dim)
                v_time = np.repeat(time[:, np.newaxis], len(height), axis=1)
                v_heigth = height
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
            frame["height"] = np.append(frame["height"], v_heigth.flatten())
            frame["name"] = np.append(frame["name"], [v] * nrows)

    df = pd.DataFrame(frame)

    # sort the data by time
    df.sort_values(by=["name", "time", "height"], inplace=True)
    df.reset_index(inplace=True, drop=True)

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

    return df


def stats(config):
    model_output_dir = config.get("model_output_dir")
    experiment_name = config.get("experiment_name")
    file_regex = config.get("file_regex")
    ensemble = config.getboolean("ensemble")
    check_variable_names = config.get("check_variable_names").split(",")
    time_dim = config.get("time_dim")
    height_dim = config.get("height_dim")
    hor_dims = config.get("hor_dims").split(",")
    stats_file_name = config.get("stats_file_name")

    if ensemble:
        seeds = config.get("seeds").split(",")
        experiments = [experiment_name + exp_modifier.format(seed=s) for s in seeds]
    else:
        experiments = [experiment_name]

    for exp in experiments:
        input_dir = "{}/{}".format(model_output_dir, exp)
        # load all model output data files matching the regex
        input_files = file_names_from_regex(input_dir, file_regex.format(exp=exp))
        if len(input_files) < 1:
            print("no files found in '{}' for regex '{}'".format(input_dir, file_regex))
            sys.exit(1)

        data = [Dataset("{}/{}".format(input_dir, f), 'r') for f in input_files]

        df = create_stats_dataframe(data, check_variable_names, time_dim, height_dim, hor_dims)

        path = "{}/{}".format(input_dir, stats_file_name)
        print("writing stats file to {}.".format(path))
        df.to_csv(path_or_buf=path, sep=",", index=False)

        for d in data:
            d.close()
