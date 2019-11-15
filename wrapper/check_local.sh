#!/bin/bash

# Compiler and Experiment
COMPILER=$1
EXP=$2

# Name of the experiments with perturbed input
PERT_EXP=${EXP}_seed_{seed}

# load machine specific settings
source probtest/wrapper/setup_machine.sh

CUR_DIR=$(pwd)/experiments/${EXP}
LOCAL_REF_DIR=$3/experiments/${EXP}

# General setup for ICON
cat > config.cfg << EOF
[DEFAULT]
# the name of the experiment to be run
experiment_name = ${EXP}
# the directory where the model output is stored
model_output_dir = ${CUR_DIR}
# the name of the stats file. No absolute path here, it will always be create in the (perturbed) model_output_dir.
stats_file_name = statistics.csv
# the name of the file containing the tolerances (per timestep and variable)
tolerance_file_name = ${REFERENCE_DIR}/${COMPILER}/tolerance/${EXP}.csv
# the list of variables that is processed by stats, tolerance and check (comma separated list)
check_variable_names = ps,pfull,ta,hus,rho,ua,va,wap

[perturb]
# the amplitude of the relative perturbation
amplitude = 1e-14
# the files that need to be perturbed (comma separated list)
files = igfff00000000.nc,igfff00000000_lbc.nc,igfff00030000_lbc.nc
# the variables that are perturbed (comma separated list)
variable_names = T,QV
# for some experiments, the whole input directory needs to be copies
copy_all_files = True

[tolerance]
# relaxation factor for the tolerance values
factor = 5

[stats]
# the name (regex) of the files containing the variables to be used in the statistics file
file_regex = .*_atm_3d.*.nc
# Template for the name (regex) of the files containing the variables to be used in the statistics file. Must contain "{seed}".
perturbed_file_regex = .*atm_3d.*.nc
# For ensemble stats: the sub-directory where the ensemble outputs are
ensemble = False
# the time, height and horizontal dimensions within the model output files
time_dim = time
height_dim = height
# can be comma separated list
hor_dims = ncells

[check]
# reference file to check against
input_file_ref = ${LOCAL_REF_DIR}/statistics.csv
# current file to be tested
input_file_cur = ${CUR_DIR}/statistics.csv

[visualize]
# the plots that are created (supported: check, tolerance)
plots = check,tolerance
# the directory where the plots are stored
savedir = ${CUR_DIR}
EOF

python probtest/probtest.py config.cfg stats -o ${LOCAL_REF_DIR}
python probtest/probtest.py config.cfg stats check visualize || exit 1

