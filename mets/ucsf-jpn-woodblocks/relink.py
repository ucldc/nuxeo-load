#!/usr/bin/env python
import sys, os, woodblocks 
from lxml import etree
import pprint

""" Rename UCSF Japanese Woodblock files we got from UCB server using local IDs extracted from mets/mods """

metadata_dir = u"/apps/content/metadata/UCSF/JapaneseWoodblocks/ucb"
new_path_dir = u"/apps/content/new_path/UCSF/JapaneseWoodblocks"
pp = pprint.PrettyPrinter()

def main(argv=None):
    # iterate through the metadata files first
    files = [files for root, dirs, files in os.walk(metadata_dir)][0]
    for file in files:
        filepath = os.path.join(metadata_dir, file)
        process_object(filepath) 

def process_object(metspath):
    print "\n##", metspath, "##"

    tree = etree.parse(metspath)
    document = tree.getroot()

    #is_complex = woodblocks.get_is_complex(document)
    filename = os.path.basename(metspath)
    doc_id = filename.split('.')[0]
    struct = woodblocks.get_struct(document, doc_id)
    #pp.pprint(struct)

    parent = struct['parent']
    process_struct_info(parent, 'parents')
    for child_dict in parent['children']:
        process_struct_info(child_dict, 'children')
              
 

def process_struct_info(item_dict, level):
    if item_dict['raw_path']: # some components don't have associated files, but rather are just organizational folders. Only link if there's a file involved.
        raw_path = item_dict['raw_path'] 
        path = item_dict['path']

        new_path = os.path.join(new_path_dir, level, path)

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
