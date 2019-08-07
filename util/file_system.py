import re
import os


def file_names_from_regex(dir_name, file_regex):
    all_files = os.listdir(dir_name)
    regex = re.compile(file_regex)
    file_names = [f for f in all_files if regex.match(f)]

    return file_names
