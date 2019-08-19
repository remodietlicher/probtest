#!/usr/bin/env python
import argparse
import configparser
from util.constants import MODE_CHECK, MODE_PERTURB, MODE_STATS, MODE_TOLERANCE, MODE_RUN_ENSEMBLE, MODE_VISUALIZE
from engine.perturb import perturb
from engine.stats import stats
from engine.check import check
from engine.tolerance import tolerance
from engine.run_ensemble import run_ensemble
from visualize.visualize import visualize
import sys


def make_parser():
    description = """
    TODO: add full description
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('config', metavar='config.cfg', type=str, help='The configuration file')
    parser.add_argument('mode', metavar='mode', type=str, nargs='*',
                        help='The mode to be run in')
    parser.add_argument('-i', dest='model_input_dir', type=str, help='the model input directory')
    parser.add_argument('-o', dest='model_output_dir', type=str, help='the model output directory')
    parser.add_argument('-t', dest='tolerance_file_name', type=str, help='the full path to the tolerance file')
    parser.add_argument('--ref', dest='input_file_ref', type=str, help='check: the path to the reference file')
    parser.add_argument('--cur', dest='input_file_cur', type=str, help='check: the path to the current file')
    parser.add_argument('-r', dest='model_run_dir', type=str, help='the path to where to model is launched from')

    return parser.parse_args()


def make_default_dict_from_parser(args):
    default_dict = vars(args)
    default_dict = {key: val for key, val in default_dict.items() if key not in ['config', 'mode'] and val}
    return default_dict


def main(args):
    default_dict = make_default_dict_from_parser(args)

    config = configparser.ConfigParser(defaults=default_dict)
    config.read(args.config)

    mode = args.mode
    for m in mode:
        if m == MODE_STATS:
            stats(config[MODE_STATS])
        elif m == MODE_PERTURB:
            perturb(config[MODE_PERTURB])
        elif m == MODE_CHECK:
            check(config[MODE_CHECK])
        elif m == MODE_TOLERANCE:
            tolerance(config[MODE_TOLERANCE])
        elif m == MODE_RUN_ENSEMBLE:
            run_ensemble(config[MODE_RUN_ENSEMBLE])
        elif m == MODE_VISUALIZE:
            visualize(config)
        else:
            sys.exit("invalid mode '{}' selected. must be '{}', '{}', '{}', '{}' or '{}'"
                     .format(mode, MODE_PERTURB, MODE_CHECK, MODE_STATS, MODE_TOLERANCE, MODE_RUN_ENSEMBLE,
                             MODE_VISUALIZE))


if __name__ == "__main__":
    args = make_parser()
    main(args)
