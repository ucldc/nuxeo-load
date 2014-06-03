#!/usr/bin/env python
import omnux
from pynux import utils
import pprint
import json

api_url = 'https://digital.library.ucsf.edu/api/'

def main():
  #collection_ids = [13,10,6,9,14,8]
  collection_ids = [13]
  nx = utils.Nuxeo()

  for collection_id in collection_ids:
    with open("./ucsf_map.json") as cf:
      collection_mapping_data = json.load(cf)
    
    collection_name = omnux.get_collection_property(collection_mapping_data, collection_id, "name") 

    items_metadata = omnux.extract_items(api_url, collection_id)
    for item in items_metadata:
      path = omnux.get_item_filename(item) 
      print path


if __name__ == '__main__':
  main()
