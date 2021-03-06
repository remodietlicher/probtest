import os
from util.netcdf_io import nc4_get_copy
import numpy as np

from util.constants import exp_modifier, perturbed_model_input_subdir


def create_perturb_files(in_path, in_files, out_path):
    path = os.path.abspath(in_path)
    if not os.path.exists(out_path):
        print("creating new directory: {}".format(out_path))
        os.makedirs(out_path)
    data = [nc4_get_copy("{}/{}".format(path, f), "{}/{}".format(out_path, f))
            for f in in_files.split(",")]

    return data


def perturb_array(array, s, a):
    shape = array.shape
    np.random.seed(s)
    p = (np.random.rand(*shape) * 2 - 1) * a + 1  # *2-1: map to [-1,1), *a: rescale to amplitude, +1 perturb around 1
    parray = np.copy(array * p)
    return parray


def perturb(config):
    model_input_dir = config.get("model_input_dir")
    model_output_dir = config.get("model_output_dir")
    experiment_name = config.get("experiment_name")
    files = config.get("files")
    seeds = np.array(config.get("seeds").split(",")).astype(int)
    variable_names = config.get("variable_names").split(",")
    amplitude = config.getfloat("amplitude")

    for s in seeds:
        modified_experiment_name = experiment_name + exp_modifier.format(seed=s)
        perturbed_model_input_dir = "{}/{}/{}".format(model_output_dir, modified_experiment_name,
                                                      perturbed_model_input_subdir)
        data = create_perturb_files(model_input_dir, files, perturbed_model_input_dir)
        for d in data:
            for vn in variable_names:
                d.variables[vn][:] = perturb_array(d.variables[vn][:], s, amplitude)
            d.close()
