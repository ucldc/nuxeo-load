#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint as pp
import sys
import os
import re
import json
from pynux import utils

''' one off script for folder of simple objects at a Nuxeo path to append alt.title to title and then delete alt.title '''

def main(argv=None):
    nuxeo = utils.Nuxeo(rcfile='~/.pynuxrc')
    path = '/asset-library/UCM/Ramicova'
    children = nuxeo.children(path)
    for child in children:     
        data = nuxeo.get_metadata(uid=child['uid'])
        update_title(data, nuxeo) 

def update_title(data, nuxeo):
    """ merge title and alt_title and update in Nuxeo """
    properties = data['properties']
    uid = data['uid']
    print(uid)
    if 'ucldc_schema:alternativetitle' in properties and properties['ucldc_schema:alternativetitle']:
        alt_title = [alt for alt in properties['ucldc_schema:alternativetitle']]
        alt_title = '; '.join(alt_title)
        merged_title = "{} -- {}".format(properties['dc:title'], alt_title)
        update = {
            'properties': {
                'dc:title': merged_title,
                'ucldc_schema:alternativetitle': None 
            }
        }
        ret = nuxeo.update_nuxeo_properties(update, uid=uid)
        if not ret:
            print "no uid found"
            exit(1)
        print(".")
    else:
        print("_")

if __name__ == "__main__":
    sys.exit(main())
