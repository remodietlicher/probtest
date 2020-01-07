#!/bin/bash

# ---------------------------------------------------------------------------
# HERE YOU NEED TO SPECIFY YOUR MACHINE SETTINGS

case $(hostname) in
    *daint*)
        # Parent directory of ICON
        export ICON_DIR=$(pwd)
        # Directory where the tolerance and reference files should be stored
        export REFERENCE_DIR=/project/c14/data-eniac/icon-test-references

        # Directory where INPUT_FILES can be found
        export ICON_DATA_POOL=/users/icontest/pool/data/ICON

        # Machine specific submit
        case $USER in
            *dremo*)
                export SUBMIT='sbatch --wait --account=c15 --partition=debug'
                export PARALLEL=False
                ;;
            *jenkins*)
                export SUBMIT='sbatch --wait --account=g110'
                export PARALLEL=True
                ;;
        esac
        ;;
    *remo*)
        echo "using hostname" $(hostname)
        # Parent directory of ICON
        export ICON_DIR=/home/remo/mch/model/icon/icon_cpu
        # Directory where the tolerance and reference files should be stored
        export REFERENCE_DIR=/home/remo/mch/model/icon/icon-test-references

        # Directory where INPUT_FILES can be found
        export ICON_DATA_POOL=/usr/local/share/ICON_pool_local

        # Machine specific submit
        export SUBMIT='ksh'
        export PARALLEL=False
        ;;
esac
