#!/usr/bin/env python
import argparse
import configparser
from util.constants import MODE_CHECK, MODE_PERTURB, MODE_STATS, MODE_TOLERANCE, MODE_RUN_ENSEMBLE
from engine.perturb import perturb
from engine.stats import stats
from engine.check import check
from engine.tolerance import tolerance
from engine.run_ensemble import run_ensemble
import sys


def make_parser():
    description = """
    TODO: add full description
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('config', metavar='config.cfg', type=str, help='The configuration file')
    parser.add_argument('mode', metavar='perturb/stats/check/tolerance', type=str, nargs='*',
                        help='The mode to be run in')

    return parser.parse_args()


def main(args):
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
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
        else:
            sys.exit("invalid mode '{}' selected. must be '{}', '{}', '{}', '{}' or '{}'"
                     .format(mode, MODE_PERTURB, MODE_CHECK, MODE_STATS, MODE_TOLERANCE, MODE_RUN_ENSEMBLE))


if __name__ == "__main__":
    args = make_parser()
    main(args)
