import sys
import os
import argparse
import json

SETS = {
    'hdl_10575_12033': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/Publications/Anthill'
        }
    }

def main():
    parser = argparse.ArgumentParser(
        description='Map metadata to ucldc schema and write to jsonl file')
    parser.add_argument('setid', help="OAI-PMH set id")
    argv = parser.parse_args()

    setid = argv.setid

    metadata_file = f"json_files/{setid}-unmapped-md.jsonl"

    # read in jsonl file
    with open(metadata_file) as mf:
        data = json.load(mf)

    # payload file
    payload_file = f"json_files/{setid}-payload.jsonl"
    if os.path.exists(payload_file):
        os.remove(payload_file)

    items = []
    for record in data:

        # get handle ID
        handle_id = [identifier for identifier in record.get('identifier') if 'hdl.handle.net' in identifier][0]

        # get something to match on
        pdf_filename = [os. path. basename(cr['ref']) for cr in record.get('component_resources')][0]
        if not pdf_filename.startswith('LD781I7S65_'):
            pdf_filename = f"LD781I7S65_{pdf_filename}"

        items.append(
                {
                    'handle_id': handle_id, 
                    'pdf_filename': pdf_filename,
                    'nuxeo_folder': SETS[setid]['nuxeo_folder']
                }
            )

    with open(payload_file, 'a') as f:
        f.write(f"{json.dumps(items)}\n")

if __name__ == '__main__':
    sys.exit(main())