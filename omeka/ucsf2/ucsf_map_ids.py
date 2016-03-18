#!/usr/bin/env python
#coding=utf-8
import omnux
import json
import codecs

API_URL = 'https://digital.library.ucsf.edu/api/'

''' map dublin core `Identifier` to Omeka Item `id` '''
def main():
    metadata = {}
    sources = []

    collection_id = 0 # all collections
    items_metadata = omnux.extract_items(API_URL, collection_id)

    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(items_metadata)

    for item in items_metadata:
        omeka_id = item['id']
        dc_identifier = ''
        source = ''
        element_texts = item['element_texts']
        for element in element_texts:
            text, element_set_name, element_name = omnux.get_element_text(element)
            if element_name == 'Identifier':
                dc_identifier = text
            if element_name == 'Source':
                source = text
                if source not in sources:
                    sources.append(source)

        if dc_identifier:
            metadata[dc_identifier] = {'omeka_id': omeka_id, 'source': source}

    with codecs.open('ucsf_sources.json', 'w', 'utf-8') as fp:
        for s in sorted(sources):
            fp.write(s)
            fp.write('\n')

    j = json.dumps(metadata, indent=4)
    with open('ucsf_id_map.json', 'w') as fp:
        fp.write(j)    
 
if __name__ == '__main__':
    main()
