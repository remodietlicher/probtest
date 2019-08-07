import os
from util.netcdf_io import nc4_get_copy
import numpy as np


def create_perturb_files(in_path, in_files, seed):
    path = os.path.abspath(in_path)
    perturb_path = path + "/perturb_{}".format(seed)
    if not os.path.exists(perturb_path):
        os.mkdir(perturb_path)
    data = [nc4_get_copy("{}/{}".format(path, f), "{}/{}".format(perturb_path, f))
            for f in in_files.split(",")]

    return data


def perturb_array(array, s, a):
    shape = array.shape
    np.random.seed(s)
    p = (np.random.rand(*shape) * 2 - 1) * a + 1  # *2-1: map to [-1,1), *a: rescale to amplitude, +1 perturb around 1
    parray = np.copy(array*p)
    return parray


def perturb(config):
    data_base_dir = config.get("data_base_dir")
    files = config.get("files")
    seeds = np.array(config.get("seeds").split(",")).astype(int)
    variable_names = config.get("variable_names").split(",")
    amplitude = config.getfloat("amplitude")

    for s in seeds:
        data = create_perturb_files(data_base_dir, files, s)
        for d in data:
            for vn in variable_names:
                d.variables[vn][:] = perturb_array(d.variables[vn][:], s, amplitude)

    for d in data:
        d.close()
