import os
import subprocess
import time
import re
import numpy as np


def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def is_none(string):
    if string.lower() in ["none", "0", "false"]:
        return True
    else:
        return False


# replace an assignment statement (left=*right* to left=new)
# "right" is used here to identify multiple assignments of "left"
def replace_assignment(line, left, right_new, right_old, seed, amplitude):
    replace = (left in line) and not line.strip().startswith("#")
    if right_old:
        replace = replace and (right_old in line)
    # make sure this is a regular assign statement (X = Y)
    replace = replace and len(line.split("=")) == 2

    if replace:
        lhs, rhs = line.split("=")
        rhs = rhs.strip()

        # if the RHS is a float, perturb
        if is_float(rhs) and not right_new:
            np.random.seed(seed)
            # *2-1: map to [-1,1), *a: rescale to amplitude, +1 perturb around 1
            p = (np.random.rand() * 2 - 1) * amplitude + 1
            right_new = float(rhs) * p
        else:
            right_new = right_new.format(seed=seed)

        out_line = "{}={}\n".format(left, right_new)
        print("replacing {} by {}".format(rhs, right_new))
    else:
        out_line = line
    return out_line


# replace all strings matching "old" substring by "new" substring
def replace_string(line, old, new):
    out_line = re.sub(old, new, line) if old in line else line
    return out_line


def prepare_perturbed_run_script(runscript, perturbed_runscript, experiment_name, modified_experiment_name,
                                 lhs, rhs_new, rhs_old, seed, amplitude):
    in_file = open(runscript, 'r')
    out_file = open(perturbed_runscript, 'w')

    for line in in_file:
        # replace input directory with the ones given in config file
        for l, ro, rn in zip(lhs, rhs_old, rhs_new):
            ro = None if is_none(ro) else ro
            rn = None if is_none(rn) else rn
            out_line = replace_assignment(line, l, rn, ro, seed, amplitude)

        # rename the experiment name
        if line == out_line:
            out_line = replace_string(line, experiment_name, modified_experiment_name)
        out_file.write(out_line)

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
    experiment_name = config.get("experiment_name")
    perturbed_experiment_name = config.get("perturbed_experiment_name")
    submit_command = config.get("submit_command")
    seeds = np.array(config.get("seeds").split(",")).astype(int)
    parallel = config.getboolean("parallel")
    dry = config.getboolean("dry")

    lhs = config.get("lhs").split(",")
    rhs_new = config.get("rhs_new").split(",")
    rhs_old = config.get("rhs_old").split(",")

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
                                     experiment_name, perturbed_experiment_name.format(seed=s),
                                     lhs, rhs_new, rhs_old,
                                     s, 1e-14)

        job = submit_command.split(" ") + [perturbed_run_script_name.format(seed=s)]

        print("running the model with '{}'".format(" ".join(job)))
        append_job(job, job_list, dry, parallel)

    finalize_jobs(job_list, dry, parallel)

    print("model finished!")
