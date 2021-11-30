import os
import sys
import logging
import argparse
from nuxeo.client import Nuxeo
from nuxeo.exceptions import HTTPError
import json
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

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
            title = item['title']
            escaped_title = title.replace('"', '""')
            no_matches.append(f"\"{item['handle_id']}\",\"{escaped_title}\",\"{item['filenames']}\"")
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
        try:
            doc = nuxeo.documents.get(path=doc_path)
        except HTTPError:
            continue

    return doc

def get_nuxeo_doc_by_title(item, nuxeo_folder, nuxeo):
    
    doc = None

    # try to get doc with same dc:title
    title = item['title']
    query = f"SELECT * FROM Document WHERE ecm:path STARTSWITH '{item['nuxeo_folder']}' AND dc:title = '{title}' AND ecm:isTrashed = 0"
    url = u'/'.join([API_BASE, API_PATH, "path/@search"])
    params = {
        'query': query
    }

    retry_strategy = Retry(
        total=3,
        status_forcelist=[413, 429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    # timeouts based on those used by nuxeo-python-client
    # see: https://github.com/nuxeo/nuxeo-python-client/blob/master/nuxeo/constants.py
    # but tweaked to be slightly larger than a multiple of 3, which is recommended
    # in the requests documentation.
    # see: https://docs.python-requests.org/en/master/user/advanced/#timeouts
    timeout_connect = 12.05
    timeout_read = (60 * 10) + 0.05
    response = http.get(url,
                auth=('Administrator', NUXEO_PASSWORD),
                headers=NUXEO_REQUEST_HEADERS,
                params=params,
                timeout=(timeout_connect, timeout_read)
                )
    response.raise_for_status()
    json_response = response.json()

    if len(json_response['entries']) == 1:
        path = json_response['entries'][0]['path']
        doc = nuxeo.documents.get(path=path)

    # try to get doc with title as basepath
    if not doc:
        doc_path = f"{nuxeo_folder}/{title}"
        try:
            doc = nuxeo.documents.get(path=doc_path)
        except HTTPError:
            doc = None    

    return doc

if __name__ == '__main__':
    sys.exit(main())