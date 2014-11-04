#!/usr/bin/env python
import sys, os
import pprint

""" Hardlink UCM LIJA no metadata files for loading into Nuxeo """

raw_dir = u"/apps/content/raw_files/UCM/JAC Newsletters/Masters/"
new_path_dir = u"/apps/content/new_path/UCM/JACNewsletters"
pp = pprint.PrettyPrinter()

def main(argv=None):
    places = [dirs for root, dirs, file in os.walk(raw_dir)][0]
    #pp.pprint(places)
    for place in places:
        place_dir = os.path.join(raw_dir, place)
        files = [files for root, dirs, files in os.walk(place_dir)][0]
        files = [f for f in files if not f[0] == '.' and f.endswith('.tif')]
        for file in files:
            folder = file.split('p')[0]
            raw_path = os.path.join(place_dir, file)
            new_path = os.path.join(new_path_dir, folder, file)
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
