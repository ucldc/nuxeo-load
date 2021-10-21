import sys
import os
import argparse
import json

SETS = {
    'hdl_10575_12033': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/Publications/Anthill'
        },
    'hdl_10575_11968': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/Publications/Yearbooks'
        },
    'hdl_10575_8408': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/Publications/Promotional Publications'
        },
    'hdl_10575_5263': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/Publications/New University'
        },
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
        pdf_filename = [os.path.basename(cr['ref']) for cr in record.get('component_resources')]
        if pdf_filename:
            pdf_filename = pdf_filename[0]
        else:
            print(f"No pdf_filename for {record['identifier']=}")

        if setid == 'hdl_10575_12033':
            if not pdf_filename.startswith('LD781I7S65_'):
                pdf_filename = f"LD781I7S65_{pdf_filename}"
        elif setid == 'hdl_10575_11968':
            pdf_filename.lstrip('LD781I7S65_')
            pdf_filename = f"{pdf_filename[0:18]}.pdf"
        elif setid == 'hdl_10575_8408':
            if pdf_filename == 'UCITheFirstDecade.pdf':
                pdf_filename = 'The First Decade%3A 1965-1975.1491586207490'
        elif setid == 'hdl_10575_5263':
            if 'http://hdl.handle.net/10575/6084' in handle_id:
                pdf_filename = 'LH1C215S64_19710219.pdf'
            elif 'http://hdl.handle.net/10575/6360' in handle_id:
                pdf_filename = 'LH1C215S64_19760406.pdf'
            elif 'http://hdl.handle.net/10575/11995' in handle_id:
                pdf_filename = 'uci_newspapers_satire_vol-16_screw_university.pdf'
            elif 'http://hdl.handle.net/10575/11998' in handle_id:
                pdf_filename = 'uci_newspapers_satire_vol-17_phew_university.pdf'
            elif 'http://hdl.handle.net/10575/11996' in handle_id:
                pdf_filename = 'uci_newspapers_satire_vol-22_the_only_alternative.pdf'
            elif 'http://hdl.handle.net/10575/11997' in handle_id:
                pdf_filename = 'uci_newspapers_satire_vol-23_the_pee_u.pdf'

            if pdf_filename.endswith('_pdfa.pdf'):
                pdf_filename = pdf_filename.rstrip('_pdfa.pdf')
                pdf_filename = f"LH1C215S64_{pdf_filename}.pdf"

        title = record.get('title')[0]

        items.append(
                {
                    'handle_id': handle_id, 
                    'pdf_filename': pdf_filename,
                    'nuxeo_folder': SETS[setid]['nuxeo_folder'],
                    'title': title
                }
            )

    with open(payload_file, 'a') as f:
        f.write(f"{json.dumps(items)}\n")

if __name__ == '__main__':
    sys.exit(main())