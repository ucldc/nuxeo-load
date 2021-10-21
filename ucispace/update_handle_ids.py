import os
import sys
import logging
import argparse
from nuxeo.client import Nuxeo
from nuxeo.exceptions import HTTPError
import json

API_BASE = 'https://nuxeo.cdlib.org/Nuxeo/site'
API_PATH = 'api/v1'
NUXEO_USER = 'Administrator'
NUXEO_PASSWORD = os.environ.get('NUXEO_PASS')

def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Update Nuxeo objects with handle IDs')
    parser.add_argument('setid', help="OAI-PMH set id")
    argv = parser.parse_args()

    setid = argv.setid

    # https://nuxeo.github.io/nuxeo-python-client/latest/#
    nuxeo = Nuxeo(
        auth=('Administrator', NUXEO_PASSWORD), 
        host=API_BASE,
        api_path=API_PATH
        )

    with open(f'json_files/{setid}-payload.jsonl', 'r') as f:
        items_metadata = json.load(f)

    for item in items_metadata:
        nuxeo_folder = item['nuxeo_folder']
        nuxeo_folder = nuxeo_folder.replace(
                '/asset-library/UCI/',
                '/asset-library/workspaces/barbara_test/'
            )
        pdf_filename = item['pdf_filename']
        doc_path = f"{nuxeo_folder}/{pdf_filename}"
        doc_url = f"{API_BASE}/{API_PATH}/path{nuxeo_folder}/{pdf_filename}"
        handle_id = item['handle_id']
        try:
            doc = nuxeo.documents.get(path=doc_path)
        except HTTPError:
            if setid == 'hdl_10575_5263':
                try:
                    alt_filename = f"LH1C215S64_{pdf_filename}"
                    doc_path = f"{nuxeo_folder}/{alt_filename}"
                    doc = nuxeo.documents.get(path=doc_path)
                except HTTPError:
                    print(f"Nuxeo doc does not exist for {pdf_filename} OR {alt_filename}, {item['title']}, {handle_id}")
                    continue

        local_id = doc.get('ucldc_schema:localidentifier')
        if handle_id not in local_id:
            local_id.append(item['handle_id'])
            doc.properties['ucldc_schema:localidentifier'] = local_id
            doc.save()
            print(f"updated {doc_path}")

if __name__ == '__main__':
    sys.exit(main())