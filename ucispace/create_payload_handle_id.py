import sys
import os
import argparse
import json
from collections import Counter

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
    'hdl_10575_12031': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/Publications/Spectre'
        },
    'hdl_10575_12030': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/Publications/Spectrum'
        },
    'hdl_10575_12885': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/Publications/Daily Pilot'
        },
    'hdl_10575_12884': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/Publications/Newporter'
        },
    'hdl_10575_12032': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/Publications/Tongue'
        },
    'hdl_10575_12019': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-063/UCI Athletics News Releases'
        },
    'hdl_10575_12018': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/Publications/Course Catalogs'
        },
    'hdl_10575_5260': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-056/Publish/Photographs'
        },
    'hdl_10575_11427': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-164'
        },
    'hdl_10575_5262': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-061/Slides'
        },
    'hdl_10575_5261': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-061/StaffPhotographerImages'
        },
    'hdl_10575_11417': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-144/AS-144_Schuyler_anteater-u.mp3'
        },
    'hdl_10575_5256': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-033/ForCalisphere'
        },
    'hdl_10575_5255': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-145'
        },
    'hdl_10575_11986': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-152'
        },
    'hdl_10575_12034': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-179/PUBLISH'
        },
    'hdl_10575_5881': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-136/AS136-014-U.mp4'
        },
    'hdl_10575_12886': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-027/Publish/California College of Medicine Films'
        },
    'hdl_10575_5257': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-158'
        },
    'hdl_10575_5259': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-020/Publish'
        },
    'hdl_10575_13154': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-182/PUBLISH'
        },
    'hdl_10575_13304': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-190'
        },
    'hdl_10575_14165': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/Filming of Planet of the Apes video'
        },
    'hdl_10575_13226': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-081'
        },
    'hdl_10575_5258': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/AS-136'
        },
    'hdl_10575_1076': {
        'nuxeo_folder': '/asset-library/UCI/SCA_UniversityArchives/Publications/Jaded'
        },
    'hdl_10575_10876': {
        'nuxeo_folder': '/asset-library/UCI/SCA_SpecialCollections/MS-F034/Lacedonia'
        },
    'hdl_10575_10878': {
        'nuxeo_folder': '/asset-library/UCI/SCA_SpecialCollections/MS-F034/Orange_County_Housecleaners'
        },
    'hdl_10575_9882': {
        'nuxeo_folder': '/asset-library/UCI/SCA_SpecialCollections/MS-R035/McMillan'
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
    all_filenames = []
    all_titles = []
    for record in data:

        # get handle ID
        handle_id = [identifier for identifier in record.get('identifier') if 'hdl.handle.net' in identifier][0]

        # get something to match on
        filenames = [os.path.basename(cr['ref']) for cr in record.get('component_resources')]
        if len(filenames) == 0 or filenames is None:
            print(f"No filenames for {record['identifier']=}")

        if setid == 'hdl_10575_12033':
            if not filenames[0].startswith('LD781I7S65_'):
                filenames = [f"LD781I7S65_{filenames[0]}"]
        elif setid == 'hdl_10575_11968':
            filename = filenames[0]
            filename.lstrip('LD781I7S65_')
            filename = f"{filename[0:18]}.pdf"
            filenames = [filename]
        elif setid == 'hdl_10575_8408':
            if filenames == ['UCITheFirstDecade.pdf']:
                filenames = ['The First Decade%3A 1965-1975.1491586207490']
        elif setid == 'hdl_10575_5263':
            if 'http://hdl.handle.net/10575/6084' in handle_id:
                filenames = ['LH1C215S64_19710219.pdf']
            elif 'http://hdl.handle.net/10575/6360' in handle_id:
                filenames = ['LH1C215S64_19760406.pdf']
            elif 'http://hdl.handle.net/10575/11995' in handle_id:
                filenames = ['uci_newspapers_satire_vol-16_screw_university.pdf']
            elif 'http://hdl.handle.net/10575/11998' in handle_id:
                filenames = ['uci_newspapers_satire_vol-17_phew_university.pdf']
            elif 'http://hdl.handle.net/10575/11996' in handle_id:
                filenames = ['uci_newspapers_satire_vol-22_the_only_alternative.pdf']
            elif 'http://hdl.handle.net/10575/11997' in handle_id:
                filenames = ['uci_newspapers_satire_vol-23_the_pee_u.pdf']
            if filenames[0].endswith('_pdfa.pdf'):
                filenames[0] = filenames[0].rstrip('_pdfa.pdf')
                filenames[0] = f"LH1C215S64_{filenames[0]}.pdf"

        all_filenames.extend(filenames)

        # get title
        title = record.get('title')
        if title:
            title = title[0]
            all_titles.append(title)
        else:
            print(f"no title for {handle_id}")

        items.append(
                {
                    'handle_id': handle_id, 
                    'filenames': filenames,
                    'nuxeo_folder': SETS[setid]['nuxeo_folder'],
                    'title': title
                }
            )

    # check for non-unique values
    all_filenames_set = set(all_filenames)
    if len(all_filenames) != len(all_filenames_set):
        print(f"Collection contains non-unique filenames")
        filename_counter = Counter(all_filenames)
        duplicate_filenames = [key for key in Counter(all_filenames).keys() if Counter(all_filenames)[key]>1]
        print(f"{duplicate_filenames}")

        for item in items:
            for filename in item['filenames']:
                if filename in duplicate_filenames:
                    item['filenames'].remove(filename)
                    item['filenames'].append(f"{filename} -- DUPLICATE")

    all_titles_set = set(all_titles)
    if len(all_titles) != len(all_titles_set):
        print(f"Collection contains non-unique titles")
        titles_counter = Counter(all_titles)
        duplicate_titles = [key for key in Counter(all_titles).keys() if Counter(all_titles)[key]>1]
        print(f"{duplicate_titles=}")

        for item in items:
            if item['title'] in duplicate_titles:
                item['title'] = f"{item['title']} -- DUPLICATE"

    with open(payload_file, 'a') as f:
        f.write(f"{json.dumps(items)}\n")

if __name__ == '__main__':
    sys.exit(main())