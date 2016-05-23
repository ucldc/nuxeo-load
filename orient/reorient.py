#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" rotate tiff images with imagemagick """

import argparse
import imghdr
import os
import sys

def is_dir(dirname):
    # https://gist.github.com/brantfaircloth/1443543
    """Checks if a path is an actual directory"""
    if not os.path.isdir(dirname):
        msg = "{0} is not a directory".format(dirname)
        raise argparse.ArgumentTypeError(msg)
    else:
        return dirname


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=is_dir)
    parser.add_argument('--do_it', default=False, action='store_true')

    if argv is None:
        argv = parser.parse_args()

    for dirpath, dirnamed, filenames in os.walk(argv.path):
        for f in filenames:
            fullpath = os.path.join(dirpath, f)
            if imghdr.what(fullpath) == 'tiff':
                orient(fullpath, argv.do_it)


def orient(tiffpath, do_it):
    print(tiffpath)
    # run `identify -format "%[orientation]" ` via subprocess
    # check for a value other than "RightTop"
    # if not RightTop and do_it:
        # copy the file (preserving metadata)
        # `convert` with -auto-orient set


# main() idiom for importing into REPL for debugging
if __name__ == "__main__":
    sys.exit(main())


"""
Copyright © 2016, Regents of the University of California
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
- Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
- Neither the name of the University of California nor the names of its
  contributors may be used to endorse or promote products derived from this
  software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""
