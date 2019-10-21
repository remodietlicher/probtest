import os
import shutil
from util.netcdf_io import nc4_get_copy
import numpy as np


def create_perturb_files(in_path, in_files, out_path, copy_all_files=False):
    path = os.path.abspath(in_path)
    if not os.path.exists(out_path):
        print("creating new directory: {}".format(out_path))
        os.makedirs(out_path)
    data = [nc4_get_copy("{}/{}".format(path, f), "{}/{}".format(out_path, f))
            for f in in_files]

    if copy_all_files:
        all_files = os.listdir(path)
        # disregard the input files which are copied above
        other_files = [f for f in all_files if f not in in_files]
        # copy all other files
        for f in other_files:
            shutil.copy("{}/{}".format(in_path, f), out_path)

    return data


def perturb_array(array, s, a):
    shape = array.shape
    np.random.seed(s)
    p = (np.random.rand(*shape) * 2 - 1) * a + 1  # *2-1: map to [-1,1), *a: rescale to amplitude, +1 perturb around 1
    parray = np.copy(array * p)
    return parray


def perturb(config):
    model_input_dir = config.get("model_input_dir")
    perturbed_model_input_dir = config.get("perturbed_model_input_dir")
    files = config.get("files").split(",")
    seeds = np.array(config.get("seeds").split(",")).astype(int)
    variable_names = config.get("variable_names").split(",")
    amplitude = config.getfloat("amplitude")
    copy_all_files = config.getboolean("copy_all_files")

    for s in seeds:
        perturbed_model_input_dir_seed = perturbed_model_input_dir.format(seed=s)
        data = create_perturb_files(model_input_dir, files, perturbed_model_input_dir_seed, copy_all_files)
        for d in data:
            for vn in variable_names:
                d.variables[vn][:] = perturb_array(d.variables[vn][:], s, amplitude)
            d.close()
