#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""migrate nuxeo data to s3"""
import sys
import argparse
import os
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import logging
import time


def main(argv=None):
    _loglevel_ = 'WARNING'
    parser = argparse.ArgumentParser(description='migrate nuxeo data to s3')
    parser.add_argument('--binaries_data',
                        required=True,
                        help="path to Nuxeo's .../nxserver/data/binaries/data")
    parser.add_argument('--bucket',
                        required=True,
                        help="s3 bucket on AWS")
    parser.add_argument(
        '--loglevel',
        default=_loglevel_,
        help=''.join([
            'CRITICAL ERROR WARNING INFO DEBUG NOTSET, default is ',
            _loglevel_
        ])
    )

    if argv is None:
        argv = parser.parse_args()

    # set debugging level
    numeric_level = getattr(logging, argv.loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % argv.loglevel)
    logging.basicConfig(level=numeric_level, )
    logger = logging.getLogger(__name__)
    # set up tuple to hold stats counters
    state_for_stats = [0.0, 0]  # sum, counter

    # find all the files in the directory
    for (dirpath, ____, filenames) in os.walk(argv.binaries_data):
        for filename in filenames:
            # upload to s3
            check_file(os.path.join(dirpath, filename),
                       filename,
                       argv.bucket,
                       logger,
                       state_for_stats)


def check_file(path, filename, bucket_name, logger, state_for_stats):
    """check if file has been uploaded; if so, double checks size"""
    conn = S3Connection()
    bucket = conn.get_bucket(bucket_name)
    key = bucket.get_key(filename)
    size = os.stat(path).st_size
    # check if this one has been uploaded yet
    if key:
        # looks like it is here; let's double check the size
        if os.stat(path).st_size != key.size:
            raise FileSizeMismatch('key exists; but sizes mis-match')
        logging.info('{0} skipped'.format(filename))
    else:
        start = time.time()
        upload(path, filename, size, bucket)
        seconds = time.time() - start
        rate = size//seconds
        state_for_stats[0] = state_for_stats[0] + size
        state_for_stats[1] = state_for_stats[1] + seconds
        average = state_for_stats[0] // state_for_stats[1]
        logging.info(
            '{0} uploaded {1:.2E} bytes in {2:.2E} '
            'seconds {3:.2E} bytes/second {4:.2E}'.format(
                filename,
                size,
                seconds,
                rate,
                average
            )
        )


def upload(path, filename, size, bucket):
    """upload file and double check size"""
    k = Key(bucket)
    k.key = filename
    k.set_contents_from_filename(path)
    # double check the size
    if k.size != size:
        raise FileSizeMismatch('something is very wrong')
    # check the md5, nuxeo uses the md5 as the filename
    if k.md5 != filename:
        raise FixityCheckError(
            'checksums mismatch {0}!={1}'.format(k.md5, filename)
        )


class FileSizeMismatch(Exception):
    pass


class FixityCheckError(Exception):
    pass


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
