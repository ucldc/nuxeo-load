#! /usr/bin/env python
#coding=utf-8
import omnux
import json
OMEKA_API = u'https://digital.library.ucsf.edu/api/'

items_metadata = omnux.extract_items(OMEKA_API, 15)
with open('omeka_md_berne.json', 'w') as f:
    json.dump(items_metadata, f, indent=3)
