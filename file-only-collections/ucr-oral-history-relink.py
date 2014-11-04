#!/usr/bin/env python
import sys, os
import pprint

""" Hardlink UCR Oral History Interviews files for loading into Nuxeo """

raw_dir = u"/apps/content/raw_files/UCR/oral history interviews/"
new_path_dir = u"/apps/content/new_path/UCR/OralHistoryInterviews/"
pp = pprint.PrettyPrinter()

def main(argv=None):
    parents = [dirs for root, dirs, files in os.walk(raw_dir)][0]
    for parent in parents:
        top_dir = os.path.join(raw_dir, parent)
        process_dir(top_dir, parent)
        mid_dirs = [dirs for root, dirs, files in os.walk(top_dir)][0]
        for mid_dir in mid_dirs:
            process_dir(os.path.join(top_dir, mid_dir), mid_dir)

def process_dir(dirpath, parent_folder):
    components = []
    files = [files for root, dirs, files in os.walk(dirpath)][0] 
    files = [f for f in files if not f.endswith('.docx') and not f.endswith('_clip.mpg')]
    for file in files:
        components.append(file)

    if len(components) > 1:
        subdir = "complex"
    else:
        subdir = "simple"
     
    for component in components:
        raw_path = os.path.join(dirpath, component)
        norm_name = component.replace(' ', '_')
        if subdir == "complex":
            new_path = os.path.join(new_path_dir, subdir, parent_folder, norm_name)
        else:
            new_path = os.path.join(new_path_dir, subdir, "OralHistoryInterviews", norm_name)
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
