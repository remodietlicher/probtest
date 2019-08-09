#!/usr/bin/env python
import argparse
import os
import subprocess


def make_parser():
    description = """
    TODO: add full description
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('config', metavar='config.cfg', type=str, help='The configuration file')

    return parser.parse_args()


def prepare_perturbed_run_script(in_file_name, out_file_name, init_key, ini_value,
                                 output_key, output_value, perturbed_model_input_dir, perturbed_model_output_dir):
    in_file = open(in_file_name, 'r')
    out_file = open(out_file_name, 'w')

    for line in in_file:
        if (init_key in line) and (ini_value in line) and not line.strip().startswith("#"):
            line = "{}={}\n".format(init_key, perturbed_model_input_dir)
        elif (output_key in line) and (output_value in line) and not line.strip().startswith("#"):
            line = "{}={}\n".format(output_key, output_value, perturbed_model_output_dir)
        out_file.write(line)

    print("writing model run script to: {}".format(out_file_name))
    out_file.close()
    in_file.close()

    return out_file_name


def run_ensemble(config):
    perturbed_model_input_dir = config.get("perturbed_model_input_dir")
    perturbed_model_output_dir = config.get("perturbed_model_output_dir")
    model_run_dir = config.get("model_run_dir")
    model_run_script_name = config.get("model_run_script_name")
    run_location = config.get("run_location")
    init_key, init_val = config.get("init_keyval").split(",")
    output_key, output_val = config.get("output_keyval").split(",")
    seeds = config.get("seeds").split(",")

    run_scripts = []
    for s in seeds:
        d_in = perturbed_model_input_dir.format(seed=s)
        d_out = perturbed_model_output_dir.format(seed=s)
        in_file_name = model_run_script_name.format(mod='')
        out_file_name = model_run_script_name.format(mod="_seed_{}".format(s))

        run_script = prepare_perturbed_run_script(in_file_name, out_file_name,
                                                  init_key, init_val, output_key, output_val, d_in, d_out)
        run_scripts.append(os.path.basename(run_script))

    if run_location == "local":
        submit_command = "ksh"
    elif run_location == "daint":
        submit_command = "sbatch --wait --account=c15"
    else:
        print("The testing infrastructure is not set up for '{}' yet!".format(run_location))
        return

    os.chdir(model_run_dir)
    for run_script in run_scripts:
        cmd_list = [submit_command, run_script]
        p = subprocess.Popen(cmd_list)
        print("running the module with '{} {}'".format(*cmd_list))
        p.communicate()
        print("model finished!")
