#!/usr/bin/env python
""" print pifolder commands for loading complex LIJA objects into Nuxeo """
import sys, os, pprint, subprocess
from pynux import utils

pp = pprint.PrettyPrinter()
nx = utils.Nuxeo()
local_base = '/apps/content/new_path/UCM/LIJA2/complex/'
nuxeo_base = 'asset-library/UCM/LIJA2'

def main(argv=None):

    # create LIJA2 folder with a dummy file. just for testing.
    #print "\n## LIJA2 with dummy file ##\n"
    #pifolder_command = "pifolder --leaf_type SampleCustomPicture --input_path /apps/content/new_path/UCM/LIJA2/complex/LIJA2 --target_path asset-library/UCM --folderish_type Organization"
    #print pifolder_command
    #subprocess.call(pifolder_command, shell=True)

    # PARENTS #
    print "\n## PARENTS ##\n"
    input_path = os.path.join(local_base, 'parents')
    target_path = nuxeo_base 
    skip_root_creation = 1
    pifolder_command =  get_pifolder_cmd(input_path, target_path, skip_root_creation)
    print pifolder_command
    subprocess.call(pifolder_command, shell=True) 
      
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
        subprocess.call(pifolder_command, shell=True)

        # add mid-level dirs to list of Nuxeo folders that will be created 
        mid_folders = [files for root, dirs, files in os.walk(input_path)][0]
        nuxeo_folders_created.extend([os.path.join(top_folder, mid_folder) for mid_folder in mid_folders])

    # GRANDCHILDREN #
    print "\n## GRANDCHILDREN ##\n"
    base_path = os.path.join(local_base, 'grandchildren')

    for top_folder in [dirs for root, dirs, files in os.walk(base_path)][0]:
        top_path = os.path.join(base_path, top_folder)

        mid_folders = [dirs for root, dirs, files in os.walk(top_path)][0]

        if top_folder in nuxeo_folders_created:
            # iterate through mid-level dirs
            for mid_folder in mid_folders:

                input_path = os.path.join(top_path, mid_folder) 

                if os.path.join(top_folder, mid_folder) in nuxeo_folders_created:
                    target_path = os.path.join(nuxeo_base, top_folder, mid_folder)
                    skip_root_creation = 1
                    is_organizational = 0
                else:
                    target_path = os.path.join(nuxeo_base, top_folder)
                    skip_root_creation = 0
                    nuxeo_folders_created.append(os.path.join(top_folder, mid_folder))
                    is_organizational = 1 

                pifolder_command = get_pifolder_cmd(input_path, target_path, skip_root_creation, is_organizational)    
                print pifolder_command, '\n'
                subprocess.call(pifolder_command, shell=True)

        else:
            # just load top-level dir
            input_path = top_path
            target_path = nuxeo_base
            skip_root_creation = 0
            nuxeo_folders_created.append(top_folder)
            nuxeo_folders_created.extend([os.path.join(top_folder, mid_folder) for mid_folder in mid_folders])
            pifolder_command = get_pifolder_cmd(input_path, target_path, skip_root_creation)
            print pifolder_command, '\n'
            subprocess.call(pifolder_command, shell=True)

        # iterate through mid-level dirs
        #for mid_folder in [dirs for root, dirs, files in os.walk(top_path)][0]:

            # check if top-level folder already exists on Nuxeo
            #if top_folder in nuxeo_folders_created:
                #top_exists = 1
            #else:
                #top_exists = 0

            # check if mid-level folder aleady exists on Nuxeo
            #if os.path.join(top_folder, mid_folder) in nuxeo_folders_created:
                #mid_exists = 1 
            #else:
                #mid_exists = 0

            # format the pifolder command
            #mid_path = os.path.join(top_path, mid_folder)
            #print "\ntop_path:", top_path
            #print "mid_path:", mid_path
            #print "top_exists:", top_folder, top_exists
            #print "mid_exists:", os.path.join(top_folder, mid_folder), mid_exists
            #is_organizational = 0
            #if top_exists:
            #    input_path = mid_path
            #    if mid_exists:
            #        target_path = os.path.join(nuxeo_base, top_folder, mid_folder)
            #        skip_root_creation = 1
            #    else:
            #        target_path = os.path.join(nuxeo_base, top_folder)
            #        skip_root_creation = 0
            #        nuxeo_folders_created.append(os.path.join(top_folder, mid_folder))
            #        is_organizational = 1
            #else:
            #    input_path = top_path
            #    target_path = nuxeo_base 
            #    skip_root_creation = 0
            #    nuxeo_folders_created.append(top_folder)
            #    nuxeo_folders_created.append(os.path.join(top_folder, mid_folder))
                 
            #print len(nuxeo_folders_created)
            #pp.pprint(nuxeo_folders_created)
            #print "input_path:", input_path
            #print "target_path:", target_path
            #print "skip_root_creation:", skip_root_creation
            #print "is_organizational:", is_organizational
            #pifolder_command = get_pifolder_cmd(input_path, target_path, skip_root_creation, is_organizational) 
            #print pifolder_command, '\n'
            #subprocess.call(pifolder_command, shell=True)


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
