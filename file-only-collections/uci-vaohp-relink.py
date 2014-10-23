#!/usr/bin/env python
import sys, os
import pprint

""" Hardlink UCI History oral histories files for loading into Nuxeo """

raw_dir = u"/apps/content/raw_files/UCI/VAOHP/ContentFiles/"
new_path_dir = u"/apps/content/new_path/UCI/VAOHP/"
pp = pprint.PrettyPrinter()

def main(argv=None):
    obj_nums = [dirs for root, dirs, files in os.walk(raw_dir)][0]
    for obj_num in obj_nums:
        obj_dir = os.path.join(raw_dir, obj_num)
        files = [files for root, dirs, files in os.walk(obj_dir)][0]
        for file in files:
            if file.endswith(('.mp3', '.mp4', '.pdf', '.JPG')) or (file.endswith(('.jpg', 'jpeg')) and file.count('.') == 1):
                raw_path = os.path.join(obj_dir, file)
                new_path = os.path.join(new_path_dir, obj_num, file)
                link_file(raw_path, new_path) 
            #elif file.count('.') == 1 and file != 'dublin_core.xml' and file != 'license.txt':
                    #print file


def link_file(fullpath_from, fullpath_to):
    print "link {} {}".format(fullpath_from, fullpath_to)
    _mkdir(os.path.dirname(fullpath_to))
    os.link(fullpath_from, fullpath_to)


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
