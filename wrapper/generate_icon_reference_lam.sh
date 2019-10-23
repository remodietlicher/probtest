#!/bin/bash

# Compiler and Experiment
COMPILER=$1
EXP=$2

# Name of the experiments with perturbed input
PERT_EXP=${EXP}_seed_{seed}

# load machine specific settings
source probtest/wrapper/setup_machine.sh

# General setup for ICON
cat > config.cfg << EOF
[DEFAULT]
# the directory where the model input is stored
model_input_dir = ${ICON_DATA_POOL}/mch/input/${EXP}
# Template for the directory where the perturbed model input is stored. Must contain "{seed}".
perturbed_model_input_dir = ${ICON_DIR}/experiments/${PERT_EXP}/input
# the directory where the model output is stored
model_output_dir = ${ICON_DIR}/experiments/${EXP}
# Template for the directory where the perturbed model output is stored. Must contain "{seed}".
perturbed_model_output_dir = ${ICON_DIR}/experiments/${PERT_EXP}
# the name of the experiment to be run
experiment_name = ${EXP}
# Template for the name of the perturbed experiments. Must contain "{seed}".
perturbed_experiment_name = ${PERT_EXP}
# the name of the stats file. No absolute path here, it will always be create in the (perturbed) model_output_dir.
stats_file_name = statistics.csv
# the name of the file containing the tolerances (per timestep and variable)
tolerance_file_name = ${REFERENCE_DIR}/${COMPILER}/tolerance/${EXP}.csv
# the list of variables that is processed by stats, tolerance and check (comma separated list)
check_variable_names = ps,pfull,ta,hus,rho,ua,va,wap
# seed the random perturbations. Each seed will generate a new set of input files (comma separated list)
# these also serve as ID for input/output directories
seeds = 1,2,3,4,5,6,7,8,9

[perturb]
# the amplitude of the relative perturbation
amplitude = 1e-14
# the files that need to be perturbed (comma separated list)
files = igfff00000000.nc,igfff00000000_lbc.nc,igfff00030000_lbc.nc
# the variables that are perturbed (comma separated list)
variable_names = T,QV
# for some experiments, the whole input directory needs to be copies
copy_all_files = True

[stats]
# the name (regex) of the files containing the variables to be used in the statistics file
file_regex = ${EXP}_atm_3d.*.nc
# Template for the name (regex) of the files containing the variables to be used in the statistics file. Must contain "{seed}".
perturbed_file_regex = ${PERT_EXP}_atm_3d.*.nc
# For ensemble stats: the sub-directory where the ensemble outputs are
ensemble = True
# the time, height and horizontal dimensions within the model output files
time_dim = time
height_dim = height
# can be comma separated list
hor_dims = ncells

[tolerance]
# relaxation factor for the tolerance values
factor = 5

[check]
# reference file to check against
input_file_ref = ${ICON_DIR}/experiments/${EXP}/statistics.csv
# current file to be tested
input_file_cur = ${ICON_DIR}/experiments/${PERT_EXP/\{seed\}/1}/statistics.csv

[run]
# directory from where the run is started (with "submit_command model_run_script_name")
run_dir = ${ICON_DIR}/run
# name of the original experiment runscript
run_script_name = exp.${EXP}.run
# Template for the perturbed experiment name. Must contain "{seed}".
perturbed_run_script_name = exp.${PERT_EXP}.run

# replace assignments in the runscript. For multiples, use comma separated list. Note that the new right handside can depend on {seed}
# define left handside
lhs = latbc_path
# define new right handside 
rhs_new = ${ICON_DIR}/experiments/${PERT_EXP}/input
# define old right handside (optional, put None if not needed)
rhs_old = None

# How a ICON job is submitted
submit_command = ${SUBMIT}
# can the jobs run in parallel?
parallel = ${PARALLEL}
# only generate runscripts, do not run the model
dry = True

[visualize]
# the plots that are created (supported: check, tolerance)
plots = check,tolerance
# the directory where the plots are stored
savedir = ${ICON_DIR}/experiments/${EXP}
EOF

python probtest/probtest.py config.cfg perturb run stats tolerance check || exit 1

echo copying reference from ${ICON_DIR}/experiments/${EXP}/statistics.csv to ${REFERENCE_DIR}/${COMPILER}/reference/${EXP}.csv
cp ${ICON_DIR}/experiments/${EXP}/statistics.csv ${REFERENCE_DIR}/${COMPILER}/reference/${EXP}.csv


