#!/usr/bin/env python
#coding=utf-8
import omnux
from pynux import utils
import pprint
#import logging

#logging.basicConfig(level=logging.DEBUG)
api_url = 'https://digital.library.ucsf.edu/api/'
campusunit = 'https://registry.cdlib.org/api/v1/repository/25/'
corpnames = [
  'Bass Photo Co.',
  'Bear Photo Service',
  'Board of Health',
  'Boyé Studios',
  'Brooks Photographers Bethesda, Md.',
  'California State Board of Pharmacy',
  'Johnson and Johnson Limited, Montreal Canada',
  'Johnson and Johnson, New Brunswick, NJ and Chicago, IL',
  'Kappa Lambda Society',
  'Sanitory Committee',
  'School of Pharmacy, University of California San Francisco',
  'The Medical Examiner',
  'UCSF School of Pharmacy',
  'University of California, College of Pharmacy Press Club'
]
omnux_fieldmap_json = '/usr/local/ucldc/nuxeo-load/omeka/omnux.json'
collection_mapping_json = '/usr/local/ucldc/nuxeo-load/omeka/ucsf_map.json'

def main():
  collection_ids = [13]
  nx = utils.Nuxeo()

  for collection_id in collection_ids:
      # get items metadata 
      items_metadata = omnux.extract_items(api_url, collection_id)
      print 'Number of items in items_metadata', collection_id, ':', len(items_metadata)
 
      # transform and load
      for item in items_metadata:
        payload = omnux.transform_omeka_to_ucldc(item, collection_id, omnux_fieldmap_json, collection_mapping_json, corpnames)
        if payload['path'] == '/asset-library/UCSF/30th_General_Hospital/band_53deacb64f.jpg':
          pp = pprint.PrettyPrinter()
          pp.pprint(payload)
          nx.update_nuxeo_properties(payload, path=payload['path'])
      
if __name__ == '__main__':
  main()  
