import sys
import os
import logging
import argparse
from nuxeo.client import Nuxeo
from nuxeo.exceptions import HTTPError
import csv

API_BASE = 'https://nuxeo.cdlib.org/Nuxeo/site'
API_PATH = 'api/v1'
NUXEO_USER = 'Administrator'
NUXEO_PASSWORD = os.environ.get('NUXEO_PASS')

def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Update Nuxeo objects with handle IDs using CSV file')
    parser.add_argument('setid', help="OAI-PMH set id")
    parser.add_argument('--dryrun', action='store_true', help="dry run")
    argv = parser.parse_args()

    setid = argv.setid
    dryrun = argv.dryrun

    # https://nuxeo.github.io/nuxeo-python-client/latest/#
    nuxeo = Nuxeo(
        auth=('Administrator', NUXEO_PASSWORD), 
        host=API_BASE,
        api_path=API_PATH
        )

    mapping = []
    with open(f'updated_csvs/{setid}.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            handle_id = row['Handle ID']
            permalink = row['Nuxeo link']
            uid = permalink.strip()
            uid = uid[44:80]
            mapping.append({'handle_id': handle_id, 'uid': uid})

    for map in mapping:
        uid = map['uid']
        handle_id = map['handle_id']
        doc = nuxeo.documents.get(uid=uid)
        current_local_id = doc.get('ucldc_schema:localidentifier')
        new_local_id = []
        for i in current_local_id:
            if not i.startswith('http://hdl.handle.net/10575/') and i != '':
                new_local_id.append(i)
        if handle_id not in new_local_id:
            new_local_id.append(handle_id)
        if dryrun:
            print(f"[dryrun] update {doc.path} with {new_local_id}")
        else:
            doc.properties['ucldc_schema:localidentifier'] = new_local_id
            doc.save()
            print(f"updated {doc.path} with {new_local_id}")

if __name__ == '__main__':
    sys.exit(main())