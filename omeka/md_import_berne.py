#! /usr/bin/env python
#coding=utf-8
import omnux
from pynux import utils
import json
import pprint

''' 
    batch import metadata from UCSF Omeka instance, Collection 15 into Nuxeo
    This metadata maps onto multiple 'Berne' collections in Nuxeo
'''
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
pp = pprint.PrettyPrinter()

def main():
    collection_id = 15
    with open('omeka_md_berne.json', 'r') as f:
        items_metadata = json.load(f)
    #items_metadata = omnux.extract_items(OMEKA_API, collection_id)
    print 'Number of items in items_metadata', collection_id, ':', len(items_metadata)

    # transform and load
    for item in items_metadata:
        #pp.pprint(item)
        #print '\n----------------------------------\n'
        nxpath = get_nuxeo_path(item)
        print "nxpath: {}".format(nxpath)
        '''
        payload = omnux.transform_omeka_to_ucldc(item, nxpath, FIELDMAP, COLLECTION_MAP, {}, CORPNAMES)

        pp.pprint(payload)
        '''

def get_nuxeo_path(omeka_md):
    element_texts = omeka_md['element_texts']
    for et in element_texts:
        if et['element_set']['name'] == 'Dublin Core' and et['element']['name'] == 'Identifier':
            identifier = et['text']

    print "identifier: {}".format(identifier)
    return ''

if __name__ == '__main__':
  main()
