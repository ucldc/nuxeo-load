#!/usr/bin/env python
#coding=utf-8
import omnux
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
REGISTRY_ID_MAP = {
                      "/asset-library/UCSF/AR 2015-4 School of Dentistry": 0,
                      "/asset-library/UCSF/AR 90-60 UCSF 125th Anniversary": 0, 
                      "/asset-library/UCSF/Archives Classification": 0,
                      "/asset-library/UCSF/MSS 2009-01 Eddie Leong Way": 0,
                      "/asset-library/UCSF/MSS 2013-4 Grande Vista Sanatorium": 0,
                      "/asset-library/UCSF/MSS 26-32 Saxton T. Pope": 0,
                      "/asset-library/UCSF/MSS 0085-38 Black Caucus": 0,
                      "/asset-library/UCSF/MSS 0098-64 Mary B. Olney": 0
                  }

def main(argv=None):
    parser = argparse.ArgumentParser(description='batch load metadata from Omeka onto existing collection of objects in Nuxeo')
    parser.add_argument('path', help='Nuxeo path to collection')

    if argv is None:
        argv = parser.parse_args()

    nuxeo_path = argv.path
    print "Loading metadata for objects at Nuxeo path: {}".format(nuxeo_path)

    with open(OMEKA_ID_MAP_FILE) as mapfile:
        omeka_id_map = json.load(mapfile)

    with open(FIELDMAP) as fieldmapfile:
        omeka_field_map = json.load(fieldmapfile)

    nx = utils.Nuxeo(rcfile=open(expanduser('~/.pynuxrc'),'r'))
    children = nx.children(nuxeo_path)

    ucldc_collection_id = REGISTRY_ID_MAP[nuxeo_path]
    collection_properties = get_collection_properties(ucldc_collection_id)

    for child in children:
        nxpath = child['path']
        print nxpath 
        print child['title'] 
        dc_identifier = splitext(child['title'])[0]
        print dc_identifier

        try:
            omeka_id = omeka_id_map[dc_identifier]['omeka_id']
        except KeyError:
            print "No corresponding Omeka ID found for {}. Skipping.".format(dc_identifier)
            continue

        print omeka_id
        omeka_md = omnux.extract_single_item(OMEKA_API, omeka_id)

        item_properties = {}
        for key, value in omeka_md.iteritems():
            if key == 'element_texts':
                for item in value:
                    text, element_set_name, element_name = omnux.get_element_text(item) 
                    nuxeo_fieldname = omeka_field_map["element_texts"]["element_set"][element_set_name][element_name]["name"]
                    item_properties[nuxeo_fieldname] = text
            # tags?
        
        print item_properties
 
        #print omeka_md 

        
    '''
      # get items metadata 
      items_metadata = omnux.extract_items(api_url, collection_id)
      print 'Number of items in items_metadata', collection_id, ':', len(items_metadata)
 
      # transform and load
      for item in items_metadata:
        payload = omnux.transform_omeka_to_ucldc(item, collection_id, omnux_fieldmap_json, collection_mapping_json, links, corpnames)
        pp.pprint(payload)
        try:
          uid = nx.get_uid(payload['path'])
          nx.update_nuxeo_properties(payload, path=payload['path'])
          print 'updated:', payload['path']
        except:
          print "No uid found or there was a problem with the payload. Not updated:", payload['path']
    '''

def get_collection_properties(ucldc_collection_id):

    properties = {}

    properties['ucldc_schema:collection'] = 'https://registry.cdlib.org/api/v1/collection/{}/'.format(ucldc_collection_id)
    properties['ucldc_schema:campusunit'] = 'https://registry.cdlib.org/api/v1/repository/25/'
    properties['ucldc_schema:type'] = 'image'
    properties['ucldc_schema:rightsstatus'] = 'Copyrighted'
    properties['ucldc_schema:rightsstatement'] = 'Transmission or reproduction of materials protected by copyright beyond that allowed by fair use requires the written permission of the copyright owners. Works not in the public domain cannot be commercially exploited without permission of the copyright owner. Responsibility for any use rests exclusively with the user.'
    
    return properties

if __name__ == '__main__':
  main()  
