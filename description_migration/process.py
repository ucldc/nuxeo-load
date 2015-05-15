#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint as pp
import sys
import os
import re
import json
from pynux import utils


BASE1 = u'/apps/nuxeo/workspace/description-migration/output'


def main(argv=None):
    nuxeo = utils.Nuxeo()
    for root, dirs, files in os.walk(BASE1):
        for file in files:
            json_data = open(os.path.join(root, file))
            data = json.load(json_data)
            migrate(data, nuxeo)


def migrate(data, nuxeo):
    """ migrate description back into nuxeo """
    properties = data['properties']
    uid = data['uid']
    print(uid)
    if 'ucldc_schema:description' in properties and properties['ucldc_schema:description']:
        update = { 
            'properties': {
                'ucldc_schema:description': [ {
                    'item': properties['ucldc_schema:description'],
                    'type': "scopecontent"
                } ]
            }
        }
        ret = nuxeo.update_nuxeo_properties(update, uid=uid)
        if not ret:
            print "no uid found"
            exit(1)
        #pp(ret)
        print(".")



if __name__ == "__main__":
    sys.exit(main())
