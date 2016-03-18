#!/usr/bin/env/python
import sys, os, shutil, subprocess
import argparse
import json

''' batch load UCSF objects from drive '''
base_dir = '/Volumes/Untitled/Collections\ to\ add\ from\ Omeka'
TARGET_MAP = {
                 'AR 2015-4 School of Dentistry': '/asset-library/UCSF/AR 2015-4 School of Dentistry',
                 'slides': '/asset-library/UCSF/AR 90-60 UCSF 125th Anniversary',
                 'artifact inventory': '/asset-library/UCSF/AR 90-60 UCSF 125th Anniversary',
                 'H': '/asset-library/UCSF/Archives Classification/H',
                 'N-S': '/asset-library/UCSF/Archives Classification/N-S',
                 'MSS 2009-01 Eddie Leong Way': '/asset-library/UCSF/MSS 2009-01 Eddie Leong Way',
                 'MSS 2013-4 Grande Vista Sanatorium': '/asset-library/UCSF/MSS 2013-4 Grande Vista Sanatorium',
                 'MSS 26-3 Saxton T. Pope': '/asset-library/UCSF/MSS 26-32 Saxton T. Pope',
                 'MSS 85-38 Black Caucus': '/asset-library/UCSF/MSS 0085-38 Black Caucus',
                 'MSS 98-64 Mary B. Olney': '/asset-library/UCSF/MSS 0098-64 Mary B. Olney'
             }
NX_UPFILE_COMMAND = "nx upfile -dir '{}' '{}'"
OMEKA_ID_MAP_FILE = "./map-omeka-to-local-id.json"

def main(argv=None):
    parser = argparse.ArgumentParser(description='batch load files into Nuxeo')
    parser.add_argument('dir', help='local path to directory of files to load')

    if argv is None:
       argv = parser.parse_args()

    files_dir = argv.dir
    print "Loading files from: {}".format(files_dir)

    nuxeo_path = TARGET_MAP[os.path.basename(os.path.normpath(files_dir))]
    print "Target Nuxeo path: {}".format(nuxeo_path) 

    with open(OMEKA_ID_MAP_FILE) as mapfile:
        omeka_id_map = json.load(mapfile)

    files = [files for root, dirs, files in os.walk(files_dir)][0]
    for file in files:
        filepath = os.path.join(files_dir, file)
        identifier = os.path.splitext(file)[0]

        try:
            omeka_id = omeka_id_map[identifier]['omeka_id'] 
        except KeyError:
            print "No corresponding Omeka ID found for {}. Skipping.".format(identifier)
            continue

        nx_upfile = NX_UPFILE_COMMAND.format(nuxeo_path, filepath)
        print nx_upfile
        subprocess.call(nx_upfile, shell=True) 

        print '----'

if __name__ == "__main__":
    sys.exit(main())
