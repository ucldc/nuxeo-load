#!/usr/bin/env python
#coding=utf-8
import omnux
import os
import argparse
from pynux import utils
from os.path import expanduser
from os.path import splitext
import omnux
import json

''' batch import metadata from Omeka onto existing Nuxeo objects '''
OMEKA_API = u'https://digital.library.ucsf.edu/api/'
OMEKA_ID_MAP_FILE = "./ucsf2/map-omeka-to-local-id.json"
CAMPUSUNIT = u'https://registry.cdlib.org/api/v1/repository/25/'
FIELDMAP = u'./omnux.json'
COLLECTION_MAP = u'./ucsf_map.json'
CORPNAMES = [
  u'UCSF Archives and Special Collections',
  u'Bass Photo Co.',
  u'Bear Photo Service',
  u'Board of Health',
  u'Boyé Studios',
  u'Brooks Photographers Bethesda, Md.',
  u'California State Board of Pharmacy',
  u'Johnson and Johnson Limited, Montreal Canada',
  u'Johnson and Johnson, New Brunswick, NJ and Chicago, IL',
  u'Kappa Lambda Society',
  u'Sanitory Committee',
  u'School of Pharmacy, University of California San Francisco',
  u'The Medical Examiner',
  u'UCSF School of Pharmacy',
  u'University of California, College of Pharmacy Press Club'
]

def main(argv=None):
    parser = argparse.ArgumentParser(description='batch load metadata from Omeka onto existing collection of objects in Nuxeo')
    parser.add_argument('path', help='Nuxeo path to collection')

    if argv is None:
        argv = parser.parse_args()

    nuxeo_path = argv.path
    print "Loading metadata for objects at Nuxeo path: {}\n".format(nuxeo_path)

    with open(OMEKA_ID_MAP_FILE) as mapfile:
        omeka_id_map = json.load(mapfile)

    with open(FIELDMAP) as fieldmapfile:
        omeka_field_map = json.load(fieldmapfile)

    nx = utils.Nuxeo()
    children = nx.children(nuxeo_path)

    for child in children:
        nxpath = child['path']
        print "\n", nxpath 
        dc_identifier = os.path.splitext(os.path.basename(nxpath))[0] 

        try:
            omeka_id = omeka_id_map[dc_identifier]['omeka_id']
        except KeyError:
            print "No corresponding Omeka ID found for {} -- Skipping.".format(dc_identifier)
            continue

        omeka_md = omnux.extract_single_item(OMEKA_API, omeka_id)
        payload = omnux.transform_omeka_to_ucldc(omeka_md, nuxeo_path, FIELDMAP, COLLECTION_MAP, {}, CORPNAMES)

        payload['path'] = nxpath

        '''
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(payload)
        '''

        #try:
        uid = nx.get_uid(payload['path'])
        print "Will update {}".format(uid)
        nx.update_nuxeo_properties(payload, path=payload['path'])
        print 'updated: {}'.format(payload['path'])
        '''
        except:
          print "No uid found or there was a problem with the payload. Not updated: {}".format(payload['path'])
        '''

if __name__ == '__main__':
  main()  
