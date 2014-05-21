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
    files_md = [x for x in junk['files_with_metadata'] if startswith_cc(x, file)]
    files_no = [x for x in junk['files_no_metadata']   if startswith_cc(x, file)]
    files_md = [x for x in files_md if correct_case(x).endswith('K.tif') or correct_case(x).endswith('G.mov')]
    files_no = [x for x in files_no if correct_case(x).endswith('K.tif') or correct_case(x).endswith('G.mov')]
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
    front, back = os.path.splitext(file)
    return "{}{}".format(front.upper(), back.lower())

def startswith_cc(string, start):
    return bool(string.upper().startswith(start.upper()))

if __name__ == "__main__":
    sys.exit(main())
