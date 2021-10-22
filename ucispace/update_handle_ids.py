import os
import sys
import logging
import argparse
from nuxeo.client import Nuxeo
from nuxeo.exceptions import HTTPError
import json
import requests

API_BASE = 'https://nuxeo.cdlib.org/Nuxeo/site'
API_PATH = 'api/v1'
NUXEO_USER = 'Administrator'
NUXEO_PASSWORD = os.environ.get('NUXEO_PASS')
TEST_FOLDER = '/asset-library/workspaces/barbara_test/'
TOKEN = os.environ.get('TOKEN')
NUXEO_REQUEST_HEADERS = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-NXDocumentProperties": "*",
                "X-NXRepository": "default",
                "X-Authentication-Token": TOKEN
                }

def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Update Nuxeo objects with handle IDs')
    parser.add_argument('setid', help="OAI-PMH set id")
    parser.add_argument('--dryrun', action='store_true', help="dry run")
    parser.add_argument('--testfolder', action='store_true', help="run against nuxeo test folder")
    argv = parser.parse_args()

    setid = argv.setid
    dryrun = argv.dryrun
    testfolder = argv.testfolder

    # https://nuxeo.github.io/nuxeo-python-client/latest/#
    nuxeo = Nuxeo(
        auth=('Administrator', NUXEO_PASSWORD), 
        host=API_BASE,
        api_path=API_PATH
        )

    with open(f'json_files/{setid}-payload.jsonl', 'r') as f:
        items_metadata = json.load(f)

    no_matches = []
    for item in items_metadata:

        nuxeo_folder = item['nuxeo_folder']
        if testfolder:
            nuxeo_folder = nuxeo_folder.replace(
                    '/asset-library/UCI/',
                    TEST_FOLDER
                )

        doc = get_nuxeo_doc(item, nuxeo_folder, nuxeo)
        if doc is None:
            print(f"Nuxeo doc does not exist for {item['handle_id']}, {item['title']} ")
            no_matches.append(f"\"{item['handle_id']}\",\"{item['title']}\",\"{item['filenames']}\"")
            continue
        local_id = doc.get('ucldc_schema:localidentifier')
        if item['handle_id'] not in local_id:
            local_id.append(item['handle_id'])
            if dryrun:
                print(f"[dryrun] update {doc.path}")
            else:       
                doc.properties['ucldc_schema:localidentifier'] = local_id
                doc.save()
                print(f"updated {doc.path}")

    if len(no_matches) > 0:
        filename = f"no_matches/{setid}.csv"
        f = open(filename, "a")
        csv = "\n".join([item for item in no_matches])
        f.write(f"Handle ID, Title, Filenames")
        f.write("\n")
        f.write(csv)
        f.write("\n")

def get_nuxeo_doc(item, nuxeo_folder, nuxeo):
    
    doc = get_nuxeo_doc_by_filename(item, nuxeo_folder, nuxeo)

    if doc is None:
        doc = get_nuxeo_doc_by_title(item, nuxeo_folder, nuxeo)

    return doc

def get_nuxeo_doc_by_filename(item, nuxeo_folder, nuxeo):
    doc = None
    for filename in item['filenames']:
        doc_path = f"{nuxeo_folder}/{filename}"
        doc_url = f"{API_BASE}/{API_PATH}/path{nuxeo_folder}/{filename}"
        #handle_id = item['handle_id']
        try:
            doc = nuxeo.documents.get(path=doc_path)
        except HTTPError:
            '''
            if setid == 'hdl_10575_5263':
                try:
                    alt_filename = f"LH1C215S64_{pdf_filename}"
                    doc_path = f"{nuxeo_folder}/{alt_filename}"
                    doc = nuxeo.documents.get(path=doc_path)
                except HTTPError:
                    print(f"Nuxeo doc does not exist for {pdf_filename} OR {alt_filename}, {item['title']}, {handle_id}")
                    return None
            else:
            '''
            continue

    return doc

def get_nuxeo_doc_by_title(item, nuxeo_folder, nuxeo):
    
    doc = None

    title = item['title']
    query = f"SELECT * FROM Document WHERE ecm:path STARTSWITH '{item['nuxeo_folder']}' AND dc:title = '{title}' AND ecm:isTrashed = 0"
    url = u'/'.join([API_BASE, API_PATH, "path/@search"])
    headers = NUXEO_REQUEST_HEADERS
    params = {
        'query': query
    }
    request = {'url': url, 'headers': headers, 'params': params}
    response = requests.get(**request)
    response.raise_for_status()
    json_response = response.json()

    if len(json_response['entries']) == 1:
        path = json_response['entries'][0]['path']
        doc = nuxeo.documents.get(path=path)

    return doc

if __name__ == '__main__':
    sys.exit(main())