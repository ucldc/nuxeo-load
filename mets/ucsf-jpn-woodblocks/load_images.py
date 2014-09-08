#!/usr/bin/env python
""" print pifolder commands for loading complex UCSF Japanese Woodblocks  objects into Nuxeo """
import sys, os, pprint, subprocess
from pynux import utils

pp = pprint.PrettyPrinter()
nx = utils.Nuxeo()
local_base = '/apps/content/new_path/UCSF/JapaneseWoodblocks'
nuxeo_base = 'asset-library/UCSF/JapaneseWoodblocks'

def main(argv=None):

    # PARENTS #
    print "\n## PARENTS ##\n"
    input_path = os.path.join(local_base, 'parents')
    target_path = nuxeo_base 
    skip_root_creation = 1
    pifolder_command =  get_pifolder_cmd(input_path, target_path, skip_root_creation)
    print pifolder_command
    #subprocess.call(pifolder_command, shell=True) 
      
    # get list of root folders that will be created
    nuxeo_folders_created = [files for root, dirs, files in os.walk(input_path)][0]

    # CHILDREN #
    print "\n## CHILDREN ##\n"
    base_path = os.path.join(local_base, 'children')

    for top_folder in [dirs for root, dirs, files in os.walk(base_path)][0]:
        input_path = os.path.join(base_path, top_folder)

        # see if we should create the root folder on nuxeo 
        if top_folder in nuxeo_folders_created:
            target_path = os.path.join(nuxeo_base, top_folder)
            skip_root_creation = 1
        else:
            target_path = nuxeo_base
            skip_root_creation = 0
            nuxeo_folders_created.append(top_folder)

        pifolder_command = get_pifolder_cmd(input_path, target_path, skip_root_creation)
        print pifolder_command
        #subprocess.call(pifolder_command, shell=True)

        # add mid-level dirs to list of Nuxeo folders that will be created 
        mid_folders = [files for root, dirs, files in os.walk(input_path)][0]
        nuxeo_folders_created.extend([os.path.join(top_folder, mid_folder) for mid_folder in mid_folders])



def get_pifolder_cmd(input_path, target_path, skip_root_creation, is_organizational=0):

    pifolder_cmd = "pifolder --leaf_type SampleCustomPicture --input_path {} --target_path {} --folderish_type {} {}"

    # FIXME. Sometimes top-level objects don't have an associated file but they are still of type SampleCustomPicture. 
    if skip_root_creation == 1:
        skiproot = '--skip_root_folder_creation'
    else:
        skiproot = '' 

    if is_organizational:
        folderish_type = "Organization"
    else:
        folderish_type = "SampleCustomPicture"

    formatted = pifolder_cmd.format(input_path, target_path, folderish_type, skiproot)

    return formatted 



if __name__ == "__main__":
    sys.exit(main())
