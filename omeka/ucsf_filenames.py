#!/usr/bin/env python
import omnux
from pynux import utils
import pprint
import json
import os

api_url = 'https://digital.library.ucsf.edu/api/'
outputdir = "/apps/nuxeo/code/nuxeo-load/relink/ucsf-omeka/paths"

def main():
  collection_ids = [13,10,6,9,14,8]
  nx = utils.Nuxeo()

  for collection_id in collection_ids:
    with open("./ucsf_map.json") as cf:
      collection_mapping_data = json.load(cf)
    
    collection_name = omnux.get_collection_property(collection_mapping_data, collection_id, "name") 
    output_file = os.path.join(outputdir, collection_name)
    try:
        os.remove(output_file)
    except OSError:
        pass

    items_metadata = omnux.extract_items(api_url, collection_id)
    with open(output_file, "a+") as f:
        for item in items_metadata:
            path = omnux.get_item_filename(item) 
            f.write(path + "\n")

if __name__ == '__main__':
  main()
