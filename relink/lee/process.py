#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint as pp
import sys
import os
import re

# merging two source directories into one
BASE1 = u'/apps/content/raw_files/UCM/LIJA'
BASE2 = u'/apps/content/raw_files/UCM/LIJA-no md/'
BASE3 = u'/apps/content/new_path/UCM/'


def main(argv=None):
    files_with_metadata = [files for root, dirs, files in os.walk(BASE1)][0]
    files_no_metadata = [files for root, dirs, files in os.walk(BASE2)][0]

    junk = {
        'files_with_metadata' : files_with_metadata,
        'files_no_metadata' : files_no_metadata,
    }

    with open("./paths") as f:
        for file in f:
            file_or_dir(file.rstrip('\n\r'), junk)

    
def file_or_dir(file, junk):
    if file.endswith('/'):
        process_dir(file, junk)
    else:
        process_file(file, junk)


def process_dir(file, junk):
    print "{} -> {}".format(file, file.upper())
    file = file.rstrip("/")
    files_md = [x for x in junk['files_with_metadata'] if x.startswith(file)]
    files_no = [x for x in junk['files_no_metadata'] if x.startswith(file)]
    if bool(files_md):
        print BASE1
        print files_md
    else:
        print BASE2
        print files_no

def process_file(file, junk):
    correct = correct_case(file)
    print "{} -> {}".format(file, correct)

def correct_case(file):
    front, back = file.split('.')
    return "{}.{}".format(front.upper(), back.lower())

if __name__ == "__main__":
    sys.exit(main())
