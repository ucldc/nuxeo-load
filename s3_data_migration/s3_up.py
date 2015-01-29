#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""migrate nuxeo data to s3"""
import sys
import argparse
import os
from boto.s3.connection import S3Connection
from boto.s3.key import Key


def main(argv=None):
    parser = argparse.ArgumentParser(description='migrate nuxeo data to s3')
    parser.add_argument('--binaries',
                        required=True,
                        help="path to Nuxeo's .../nxserver/data/binaries/")
    parser.add_argument('--bucket',
                        required=True,
                        help="s3 bucket on AWS")
    if argv is None:
        argv = parser.parse_args()

    for (dirpath, ____, filenames) in os.walk(argv.binaries):
        for filename in filenames:
            s3_up(os.path.join(dirpath, filename), argv.bucket)


def s3_up(filename, bucket_name):
    """upload a single file (if it does not exist)"""
    print(filename)
    conn = S3Connection()
    bucket = conn.get_bucket(bucket_name)


# main() idiom for importing into REPL for debugging
if __name__ == "__main__":
    sys.exit(main())

"""
Copyright © 2015, Regents of the University of California
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