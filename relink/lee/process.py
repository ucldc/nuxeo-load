#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint as pp
import sys
import os
import re

# merging two source directories into one
BASE1 = u'/apps/content/raw_files/UCM/LIJA'
BASE2 = u'/apps/content/raw_files/UCM/LIJA-no md/'
BASE3 = u'/apps/content/new_path/UCM/LIJA'


def main(argv=None):
    files_with_metadata = [files for root, dirs, files in os.walk(BASE1)][0]
    files_no_metadata =   [files for root, dirs, files in os.walk(BASE2)][0]

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
    file = file.rstrip("/")
    files_md = [x for x in junk['files_with_metadata'] if startswith_cc(x, file)]
    files_no = [x for x in junk['files_no_metadata']   if startswith_cc(x, file)]
    files_md = [x for x in files_md if correct_case(x).endswith('K.tif') or correct_case(x).endswith('G.mov')]
    files_no = [x for x in files_no if correct_case(x).endswith('K.tif') or correct_case(x).endswith('G.mov')]
    if bool(files_md):
        link_dir(BASE1, file, files_md)
    else:
        link_dir(BASE2, file, files_no)


def link_dir(base, dir, files):
    # create directory at BASE3
    _mkdir(os.path.join(BASE3, u'complex', dir.upper()))
    for file in files:
        link_file(base, file, u'complex', dir.upper())


def process_file(file, junk):
    files_md = [x for x in junk['files_with_metadata'] if startswith_cc(x, file)]
    files_no = [x for x in junk['files_no_metadata']   if startswith_cc(x, file)]
    if bool(files_md):
        link_file(BASE1, file, u'simple', '')
    else:
        link_file(BASE2, file, u'simple', '')


def link_file(base, file, subdir, dir):
    from_file = os.path.join(base, file)
    to_file = os.path.join(BASE3, subdir, dir, correct_case(file))
    print "link {} {}".format(from_file, to_file)
    os.link(from_file, to_file)


def correct_case(file):
    front, back = os.path.splitext(file)
    return "{}{}".format(front.upper(), back.lower())


def startswith_cc(string, start):
    return bool(string.upper().startswith(start.upper()))


# http://code.activestate.com/recipes/82465-a-friendly-mkdir/
def _mkdir(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)


if __name__ == "__main__":
    sys.exit(main())
