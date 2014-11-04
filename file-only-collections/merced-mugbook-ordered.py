#!/usr/bin/env python
import sys, os, shutil, subprocess
import pprint

""" Batch load Merced Mugbook sub-components with workaround so that they appear in Nuxeo in lexical order. """

content_dir = u"/apps/content/new_path/UCM/MercedMugbook/"
object_name = "MercedMugbook"
temp_dir = os.path.join("/apps/nuxeo/code/nuxeo-load/file-only-collections/temp-for-loading/", object_name)
target_base_path = u"/asset-library/UCM"
target_folder = os.path.join(target_base_path, object_name)

pp = pprint.PrettyPrinter()

def main(argv=None):
    _mkdir(temp_dir)
    components = [files for root, dirs, files in os.walk(content_dir)][0]
    components = sorted(components)
    count = 0
    for component in components: 

        if count == 0:
            pifolder_cmd = "pifolder --leaf_type SampleCustomPicture --input_path {} --target_path {} --folderish_type SampleCustomPicture".format(temp_dir, target_base_path)
        else:
            pifolder_cmd = "pifolder --leaf_type SampleCustomPicture --input_path {} --target_path {} --folderish_type SampleCustomPicture --skip_root_folder_creation".format(temp_dir, target_folder)

        print pifolder_cmd

        copy_from = os.path.join(content_dir, component)
        copy_to = os.path.join(temp_dir, component)
        print copy_from, copy_to
        shutil.copy(copy_from, copy_to)

        subprocess.call(pifolder_cmd, shell=True)

        os.remove(copy_to)

        count = count + 1


# http://code.activestate.com/recipes/82465-a-friendly-mkdir/
def _mkdir(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)



if __name__ == "__main__":
    sys.exit(main())
