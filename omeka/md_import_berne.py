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
BERNE_MAP = './berne_id_map.json'
with open(BERNE_MAP, 'r') as bernemapfile:
    id_map = json.load(bernemapfile)
pp = pprint.PrettyPrinter()

def main():
    collection_id = 15
    with open('omeka_md_berne.json', 'r') as f:
        items_metadata = json.load(f)
    print 'Number of items in items_metadata', collection_id, ':', len(items_metadata)

    nx = utils.Nuxeo()
    # transform and load
    missing = {}
    for item in items_metadata:
        #pp.pprint(item)
        #print '\n----------------------------------\n'
        identifier = get_identifier(item)
        nxuid = get_nuxeo_uid(identifier)
        if nxuid is None:
            missing[identifier] = item['id'] 
        else:
            nxpath = nx.get_metadata(uid=nxuid)['path']
            collection = get_nx_collection(nxpath)

            payload = omnux.transform_omeka_to_ucldc(item, collection, FIELDMAP, COLLECTION_MAP, {}, CORPNAMES)
            payload['path'] = nxpath
            #pp.pprint(payload)

            print "Will update {}".format(nxuid)
            nx.update_nuxeo_properties(payload, path=payload['path']) 
            print 'updated: {}'.format(payload['path'])

    with open('missing_berne.json', 'w') as f:
        json.dump(missing, f, indent=3)

def get_identifier(omeka_md):
    ''' given omeka metadata, get dublin core `Identifier` value '''
    element_texts = omeka_md['element_texts']
    for et in element_texts:
        if et['element_set']['name'] == 'Dublin Core' and et['element']['name'] == 'Identifier':
            identifier = et['text'].strip()

    return identifier

def get_nuxeo_uid(identifier):
    try:
        nxuid = id_map[identifier]
    except KeyError:
        nxuid = None

    return nxuid

def get_nx_collection(path):
    parts = path.split('/')[0:4]
    collection = '/'.join(parts[0:4])   
    return collection
 
if __name__ == '__main__':
  main()
