#!/bin/bash

# Compiler and Experiment
COMPILER=$1
EXP=$2

# Parent directory of ICON
ICON_DIR=$(pwd)
# Directory where the tolerance and reference files should be stored
REFERENCE_DIR=/project/c15/dremo/model/icon-test-references

# Directory where INPUT_FILES can be found
INPUT_DIR=/users/icontest/pool/data/ICON/grids/private/mpim/icon_preprocessing/source/initial_condition
# Name of the input files
INPUT_FILES=ifs2icon_1979010100_R02B04_G.nc

# Name of the experiments with perturbed input
PERT_EXP=${EXP}_seed_{seed}

# General setup for ICON
cat > config.cfg << EOF
[DEFAULT]
# the directory where the model input is stored
model_input_dir = ${INPUT_DIR}
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
files = ${INPUT_FILES}
# the variables that are perturbed (comma separated list)
variable_names = T,QV

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
input_file_ref = ${REFERENCE_DIR}/${COMPILER}/reference/${EXP}.csv
# current file to be tested
input_file_cur = ${ICON_DIR}/experiments/${EXP}/statistics.csv

[run]
# directory from where the run is started (with "submit_command model_run_script_name")
run_dir = ${ICON_DIR}/run
# name of the original experiment runscript
run_script_name = exp.${EXP}.run
# Template for the perturbed experiment name. Must contain "{seed}".
perturbed_run_script_name = exp.${PERT_EXP}.run
# key-value pair to find the line in runscript that defines the input files
init_keyval = datadir,initial_condition
# How a ICON job is submitted
submit_command = sbatch --wait --account=g110
# can the jobs run in parallel?
parallel = True
# only generate runscripts, do not run the model
dry = False

[visualize]
# the plots that are created (supported: check, tolerance)
plots = check,tolerance
# the directory where the plots are stored
savedir = ${ICON_DIR}/experiments/${EXP}
EOF

python probtest/probtest.py config.cfg perturb run stats tolerance check

echo copying reference from ${ICON_DIR}/experiments/${EXP}/statistics.csv to ${REFERENCE_DIR}/${COMPILER}/reference/${EXP}.csv
cp ${ICON_DIR}/experiments/${EXP}/statistics.csv ${REFERENCE_DIR}/${COMPILER}/reference/${EXP}.csv


