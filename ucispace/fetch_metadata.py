import os
import sys
import argparse
import json
from sickle import Sickle
from sickle.models import Record as SickleDCRecord
from lxml import etree

oai_endpoint = 'http://ucispace-prod.lib.uci.edu:8080/oai/request'
metadata_prefix = 'didl'

class SickleDIDLRecord(SickleDCRecord):

    def __init__(self, record_element, strip_ns=True):
        super(SickleDIDLRecord, self).__init__(
            record_element, strip_ns=strip_ns)
        
        ''' add the didl component attribute info to the metadata '''
        if not self.deleted:
            didl = self.xml.find('.//{urn:mpeg:mpeg21:2002:02-DIDL-NS}DIDL')
            components = didl.findall('.//{urn:mpeg:mpeg21:2002:02-DIDL-NS}Component')
            resources = []
            for c in components:
                resource = c.find('.//{urn:mpeg:mpeg21:2002:02-DIDL-NS}Resource')
                component_resource = {
                    'id': c.attrib['id'],
                    'mimeType': resource.attrib['mimeType'],
                    'ref': resource.attrib['ref']
                }
                resources.append(component_resource)
            self.metadata['component_resources'] = resources


def main():

    parser = argparse.ArgumentParser(
        description='Fetch metadata for OAI set and write jsonl file')
    parser.add_argument('setid', help="OAI-PMH set id")
    argv = parser.parse_args()

    sickle = Sickle(oai_endpoint)
    sickle.class_mapping['ListRecords'] = SickleDIDLRecord

    setid = argv.setid
    records = sickle.ListRecords(metadataPrefix=metadata_prefix, set=setid, ignore_deleted=True)

    filename = f"json_files/{setid}-unmapped-md.jsonl"
    if os.path.exists(filename):
        os.remove(filename)

    # needs to be in an array
    all_metadata = [record.metadata for record in records]

    with open(filename, 'a') as f:
        f.write(json.dumps(all_metadata))


if __name__ == '__main__':
    sys.exit(main())

