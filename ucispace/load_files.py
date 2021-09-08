import os
import sys
import logging
import argparse
from nuxeo.client import Nuxeo
from nuxeo.models import Document, FileBlob
from nuxeo.exceptions import UploadError
import json
import requests
from urllib.parse import urljoin

API_BASE = 'https://nuxeo.cdlib.org/Nuxeo/site'
API_PATH = 'api/v1'
NUXEO_USER = 'Administrator'
NUXEO_PASSWORD = os.environ.get('NUXEO_PASS')

def create_doc_with_content(content_dict, properties, nuxeo_type, nuxeo, doc_url, logger):

    # DOWNLOAD CONTENT FILE
    remote_url = content_dict['ref']
    local_file = os.path.basename(remote_url)
    mimetype = content_dict['mimeType']
    nuxeo_doc_type = content_dict['nuxeo_doc_type']
    ucldc_type = content_dict['ucldc_schema:type']

    data = requests.get(remote_url)
    data.raise_for_status()
    with open(local_file, 'wb')as file:
        file.write(data.content)

    # INITIALIZE PATH
    file_blob = FileBlob(local_file)
    batch = nuxeo.uploads.batch()

    batch_id = batch.batchId

    # upload blob
    try:
        uploaded = nuxeo.uploads.upload(batch, file_blob)
    except UploadError:
        # The blob wasn't uploaded despite the 3 retries,
        # you can handle it however you like and relaunch
        # the same command
        logging.error(UploadError)

    # CREATE DOCUMENT FROM LOADED BLOB AND ADD METADATA
    # https://doc.nuxeo.com/nxdoc/howto-upload-file-nuxeo-using-rest-api/
    headers = {'Content-Type': 'application/json'}
    auth = (NUXEO_USER, NUXEO_PASSWORD)

    if not properties.get('dc:title'):
        properties['dc:title'] = local_file
    properties['file:content'] = {
        "upload-batch": batch_id,
        "upload-fileId": "0"
    }
    data = {
        "entity-type": "document",
        "name": local_file,
        "properties": properties,
        "type": nuxeo_type}

    res = requests.post(
        doc_url,
        headers=headers,
        auth=auth,
        data=json.dumps(data)
        )
    res.raise_for_status()
    logger.debug(res.content)


    # CLEAN UP
    os.remove(local_file)

def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(
        description='Load objects file(s) and metadata into Nuxeo')
    parser.add_argument('setid', help="OAI-PMH set id")
    argv = parser.parse_args()

    setid = argv.setid

    # https://nuxeo.github.io/nuxeo-python-client/latest/#
    nuxeo = Nuxeo(
        auth=('Administrator', NUXEO_PASSWORD), 
        host=API_BASE,
        api_path=API_PATH
        )

    # GET ITEM METADATA
    with open(f'json_files/{setid}-payload.jsonl', 'r') as f:
        items_metadata = json.load(f)

    for item in items_metadata:

        nuxeo_folder = item['nuxeo_folder']
        nuxeo_folder = nuxeo_folder.replace(
                '/asset-library/UCI/',
                '/asset-library/workspaces/barbara_test/'
            )
        nuxeo_type = item['nuxeo_doc_type']
        properties = item['properties']
        doc_name = properties['dc:title']
        doc_name = properties['ucldc_schema:localidentifier'][0]
        doc_name = doc_name.lstrip('http://hdl.handle.net/')
        doc_name = doc_name.replace('/', '_')


        # CREATE PARENT DOCUMENT
        # load file + metadata
        if item.get('content_files') and item['content_files'].get('main'):
            for main_file in item['content_files']['main']:
                doc_url = f"{API_BASE}/{API_PATH}/path/{nuxeo_folder}"
                create_doc_with_content(main_file, properties, nuxeo_type, nuxeo, doc_url, logger)
        else:
            # create metadata only object
            new_file = Document(
                name=doc_name,
                type=nuxeo_type,
                properties=properties
            )

            file = nuxeo.documents.create(
                new_file,
                parent_path=nuxeo_folder
            )


        # CREATE COMPONENT DOCUMENTS
        # load file. (no component-level metadata provided)
        if item.get('content_files') and item['content_files'].get('components'):
            for component in item['content_files']['components']:
                doc_url = f"{API_BASE}/{API_PATH}/path/{nuxeo_folder}/{doc_name}"
                properties = {}
                nuxeo_type = component['nuxeo_doc_type']
                create_doc_with_content(component, properties, nuxeo_type, nuxeo, doc_url, logger)


if __name__ == '__main__':
    sys.exit(main())
