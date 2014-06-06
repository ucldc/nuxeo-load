#!/usr/bin/env python
#coding=utf-8
import omnux
from pynux import utils
import pprint
#import logging

#logging.basicConfig(level=logging.DEBUG)
api_url = u'https://digital.library.ucsf.edu/api/'
campusunit = u'https://registry.cdlib.org/api/v1/repository/25/'
corpnames = [
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
omnux_fieldmap_json = u'./omnux.json'
collection_mapping_json = u'./ucsf_map.json'
hardlinks = u'../relink/ucsf-omeka/hardlinks.txt'

def main():
  collection_ids = [13,10,6,9,14,8]
  nx = utils.Nuxeo()
  pp = pprint.PrettyPrinter()

  links = {} 
  with open(hardlinks, "r") as h:
    for line in h:
      line = line.rstrip('\n')
      line = line.split(' ')
      links[line[0]] = line[1]
  
  for collection_id in collection_ids:
      # get items metadata 
      items_metadata = omnux.extract_items(api_url, collection_id)
      print 'Number of items in items_metadata', collection_id, ':', len(items_metadata)
 
      # transform and load
      for item in items_metadata:
        payload = omnux.transform_omeka_to_ucldc(item, collection_id, omnux_fieldmap_json, collection_mapping_json, links, corpnames)
        #pp.pprint(payload)
        try:
          uid = nx.get_uid(payload['path'])
          nx.update_nuxeo_properties(payload, path=payload['path'])
          print 'updated:', payload['path']
        except:
          print "No uid found. Not updating:", payload['path']


if __name__ == '__main__':
  main()  
