import re

def nuxeo_mapper(docs, nx):
    for doc in docs:
        title = doc['properties']['dc:title']
        if title.endswith('_new.jpg'):
            print(title)
            m = re.search('_(\d\d\d)_new.jpg$', title)
            page = m.group(1).lstrip('0')
            doc['properties'] = { 'dc:title': page }
            print(doc['uid'])
            print(page) 
            nx.update_nuxeo_properties(doc, uid=doc['uid'])
