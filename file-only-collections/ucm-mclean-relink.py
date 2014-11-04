#!/usr/bin/env python
import sys, os
import pprint

""" Hardlink UCM McLean files for loading into Nuxeo """

raw_dir = u"/apps/content/raw_files/UCM/Mclean/"
new_path_dir = u"/apps/content/new_path/UCM/McLean/"
pp = pprint.PrettyPrinter()

def main(argv=None):
    obj_nums = [dirs for root, dirs, files in os.walk(raw_dir)][0]
    for obj_num in obj_nums:
        obj_dir = os.path.join(raw_dir, obj_num)
        components = []
        for root, dirs, files in os.walk(obj_dir):
            for file in files:
                if file.endswith('_k.tif') and not file.startswith('.'):
                    components.append(file)
        if len(components) > 1:
            subdir = "complex"
        else:
            subdir = "simple"
        for component in components:
            raw_path = os.path.join(obj_dir, component)
            if subdir == "complex":
                new_path = os.path.join(new_path_dir, subdir, obj_num, component)
            else:
                new_path = os.path.join(new_path_dir, subdir, "McLean", component)
            #print raw_path, new_path
            link_file(raw_path, new_path)

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
