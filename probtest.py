#!/usr/bin/env python
import argparse
import configparser
from util.constants import MODE_CHECK, MODE_PERTURB, MODE_STATS
from engine.perturb import perturb
import sys


def make_parser():
    description = """
    TODO: add full description
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('config', metavar='config.cfg', type=str, help='The configuration file')

    return parser.parse_args()


def main(args):
    config = configparser.ConfigParser()
    config.read(args.config)

    mode = config['run'].get('mode')
    if mode == MODE_STATS:
        print("stats is not yet implemented")
    elif mode == MODE_PERTURB:
        perturb(config[MODE_PERTURB])
    elif mode == MODE_CHECK:
        print("perturb is not yet implemented")
    else:
        sys.exit("invalid mode '{}' selected. must be '{}', '{}' or '{}'".format(mode, MODE_PERTURB, MODE_CHECK, MODE_STATS))


if __name__ == "__main__":
    args = make_parser()
    main(args)
