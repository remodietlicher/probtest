import os
import subprocess
import time

from util.constants import perturbed_model_input_dir, perturbed_model_output_dir


def prepare_perturbed_run_script(in_file_name, out_file_name, init_key, ini_value,
                                 output_key, output_value, d_in, d_out):
    in_file = open(in_file_name, 'r')
    out_file = open(out_file_name, 'w')

    for line in in_file:
        if (init_key in line) and (ini_value in line) and not line.strip().startswith("#"):
            line = "{}={}\n".format(init_key, d_in)
        elif (output_key in line) and (output_value in line) and not line.strip().startswith("#"):
            line = "{}={}\n".format(output_key, d_out)
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
    output_key, output_val = config.get("output_keyval").split(",")
    seeds = config.get("seeds").split(",")
    parallel = config.getboolean("parallel")
    dry = config.getboolean("dry")

    os.chdir(model_run_dir)
    procs = []
    for s in seeds:
        d_in = "{}/{}".format(model_output_dir, perturbed_model_input_dir.format(seed=s))
        d_out = "{}/{}".format(model_output_dir, perturbed_model_output_dir.format(seed=s))
        in_file_name = "{}/{}".format(model_run_dir, model_run_script_name.format(mod=''))
        out_file_name = "{}/{}".format(model_run_dir, model_run_script_name.format(mod="_seed_{}".format(s)))

        run_script = prepare_perturbed_run_script(in_file_name, out_file_name,
                                                  init_key, init_val, output_key, output_val, d_in, d_out)

        run_script = os.path.basename(run_script)
        if not os.path.exists(d_out):
            print("creating perturbed model output directory {}".format(d_out))
            os.makedirs(d_out)
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
