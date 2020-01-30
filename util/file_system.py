import re
import os
import sys


def file_names_from_regex(dir_name, file_regex):
    all_files = os.listdir(dir_name)
    regex = re.compile(file_regex)
    file_names = [f for f in all_files if regex.match(f)]
    if len(file_names) < 1:
        print("no files found in '{}' for regex '{}'".format(dir_name, file_regex))
        print("the directory contains the following files:")
        for f in all_files:
            print(f)
        sys.exit(1)

    return file_names
