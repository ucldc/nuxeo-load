#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" reorder components by name """

import sys
import argparse
import psycopg2


GET_COMPONENTS = u'''
SELECT id, name
FROM hierarchy
WHERE parentid=%s
  AND primarytype
    IN ('SampleCustomPicture', 'CustomFile', 'CustomVideo', 'CustomAudio')
ORDER BY name;
'''

REORDER = u'''
UPDATE hierarchy
SET pos=%s
WHERE id=%s;
'''


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('parentid')

    if argv is None:
        argv = parser.parse_args()

    conn = psycopg2.connect("")
    cur = conn.cursor()
    cur.execute(GET_COMPONENTS, (argv.parentid,))
    for i, row in enumerate(cur):
        myid = row[0]
        print(row)
        with conn.cursor() as inner_cur:
            inner_cur.execute(REORDER, (i, myid))
    conn.commit()


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
