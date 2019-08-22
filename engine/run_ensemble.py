import os
import subprocess
import time
import re

from util.constants import perturbed_model_input_dir, perturbed_model_output_dir


def prepare_perturbed_run_script(in_file_name, out_file_name, init_key, init_value,
                                 d_in, old_exp, new_exp):
    in_file = open(in_file_name, 'r')
    out_file = open(out_file_name, 'w')

    for line in in_file:
        # replace input directory with the one given in config file
        if (init_key in line) and (init_value in line) and not line.strip().startswith("#"):
            line = "{}={}\n".format(init_key, d_in)
        # rename the experiment name
        elif old_exp in line:
            line = re.sub(old_exp, new_exp, line)
        out_file.write(line)

    print("writing model run script to: {}".format(out_file_name))
    out_file.close()
    in_file.close()

    return out_file_name


def run_ensemble(config):
    model_run_dir = config.get("model_run_dir")
    model_run_script_name = config.get("model_run_script_name")
    model_output_dir = config.get("model_output_dir")
    submit_command = config.get("submit_command")
    init_key, init_val = config.get("init_keyval").split(",")
    old_exp, new_exp = config.get("rename_exp").split(",")
    seeds = config.get("seeds").split(",")
    parallel = config.getboolean("parallel")
    dry = config.getboolean("dry")

    os.chdir(model_run_dir)
    procs = []
    for s in seeds:
        seed_extension = "_seed_{}".format(s)
        d_in = "{}/{}".format(model_output_dir, perturbed_model_input_dir.format(seed=s))
        in_file_name = "{}/{}".format(model_run_dir, model_run_script_name.format(mod=''))
        out_file_name = "{}/{}".format(model_run_dir, model_run_script_name.format(mod=seed_extension))
        seed_exp = new_exp.format(mod=seed_extension)

        run_script = prepare_perturbed_run_script(in_file_name, out_file_name,
                                                  init_key, init_val, d_in, old_exp, seed_exp)

        run_script = os.path.basename(run_script)
        cmd_list = submit_command.format(seed=s).split(" ") + [run_script]
        if not dry:
            p = subprocess.Popen(cmd_list)
        print("running the model with '{}'".format(" ".join(cmd_list)))
        if not dry:
            if not parallel:
                p.communicate()
                time.sleep(5)
            else:
                procs.append(p)

    if parallel and not dry:
        for p in procs:
            p.communicate()
    print("model finished!")
