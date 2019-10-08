import os
import subprocess
import time
import re


def prepare_perturbed_run_script(runscript, perturbed_runscript, init_key, init_value,
                                 perturbed_model_input_dir, experiment_name, modified_experiment_name):
    in_file = open(runscript, 'r')
    out_file = open(perturbed_runscript, 'w')

    for line in in_file:
        # replace input directory with the one given in config file
        if (init_key in line) and (init_value in line) and not line.strip().startswith("#"):
            line = "{}={}\n".format(init_key, perturbed_model_input_dir)
        # rename the experiment name
        elif experiment_name in line:
            line = re.sub(experiment_name, modified_experiment_name, line)
        out_file.write(line)

    print("writing model run script to: {}".format(perturbed_runscript))
    out_file.close()
    in_file.close()

    return


def append_job(job, job_list, dry, parallel):
    if not dry:
        p = subprocess.Popen(job)
        if not parallel:
            p.communicate()
            time.sleep(5)
        else:
            job_list.append(p)


def finalize_jobs(job_list, dry, parallel):
    if parallel and not dry:
        for job in job_list:
            job.communicate()


def run_ensemble(config):
    run_dir = config.get("run_dir")
    run_script_name = config.get("run_script_name")
    perturbed_run_script_name = config.get("perturbed_run_script_name")
    perturbed_model_input_dir = config.get("perturbed_model_input_dir")
    experiment_name = config.get("experiment_name")
    perturbed_experiment_name = config.get("perturbed_experiment_name")
    submit_command = config.get("submit_command")
    init_key, init_val = config.get("init_keyval").split(",")
    seeds = config.get("seeds").split(",")
    parallel = config.getboolean("parallel")
    dry = config.getboolean("dry")

    os.chdir(run_dir)
    job_list = []

    # run the reference
    job = submit_command.split(" ") + [run_script_name]
    append_job(job, job_list, dry, parallel)

    # run the ensemble
    for s in seeds:
        runscript = "{}/{}".format(run_dir, run_script_name)
        perturbed_runscript = "{}/{}".format(run_dir, perturbed_run_script_name.format(seed=s))

        prepare_perturbed_run_script(runscript, perturbed_runscript,
                                     init_key, init_val, perturbed_model_input_dir.format(seed=s),
                                     experiment_name, perturbed_experiment_name.format(seed=s))

        job = submit_command.split(" ") + [perturbed_run_script_name.format(seed=s)]

        print("running the model with '{}'".format(" ".join(job)))
        append_job(job, job_list, dry, parallel)

    finalize_jobs(job_list, dry, parallel)

    print("model finished!")
