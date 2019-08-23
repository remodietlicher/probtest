import os
import subprocess
import time
import re

from util.constants import exp_modifier, perturbed_model_input_subdir


def prepare_perturbed_run_script(runscript, modified_runscript, init_key, init_value,
                                 perturbed_model_input_dir, experiment_name, modified_experiment_name):
    in_file = open(runscript, 'r')
    out_file = open(modified_runscript, 'w')

    for line in in_file:
        # replace input directory with the one given in config file
        if (init_key in line) and (init_value in line) and not line.strip().startswith("#"):
            line = "{}={}\n".format(init_key, perturbed_model_input_dir)
        # rename the experiment name
        elif experiment_name in line:
            line = re.sub(experiment_name, modified_experiment_name, line)
        out_file.write(line)

    print("writing model run script to: {}".format(modified_runscript))
    out_file.close()
    in_file.close()

    return


def run_ensemble(config):
    model_run_dir = config.get("model_run_dir")
    model_run_script_name = config.get("model_run_script_name")
    model_output_dir = config.get("model_output_dir")
    experiment_name = config.get("experiment_name")
    submit_command = config.get("submit_command")
    init_key, init_val = config.get("init_keyval").split(",")
    seeds = config.get("seeds").split(",")
    parallel = config.getboolean("parallel")
    dry = config.getboolean("dry")

    os.chdir(model_run_dir)
    procs = []
    for s in seeds:
        modified_experiment_name = experiment_name + exp_modifier.format(seed=s)
        perturbed_model_input_dir = "{}/{}/{}".format(model_output_dir, modified_experiment_name,
                                                      perturbed_model_input_subdir)
        runscript = "{}/{}".format(model_run_dir, model_run_script_name.format(exp=experiment_name))
        modified_runscript = "{}/{}".format(model_run_dir, model_run_script_name.format(exp=modified_experiment_name))

        prepare_perturbed_run_script(runscript, modified_runscript,
                                     init_key, init_val, perturbed_model_input_dir,
                                     experiment_name, modified_experiment_name)

        cmd_list = submit_command.format(seed=s).split(" ") + [os.path.basename(modified_runscript)]
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
