#!/usr/bin/env python
import sys, os
import pprint

""" Hardlink UCM LIJA no metadata files for loading into Nuxeo """

raw_dir = u"/apps/content/raw_files/UCM/LIJA-no md/"
new_path_dir = u"/apps/content/new_path/UCM/LIJA-no-md/"
pp = pprint.PrettyPrinter()

def main(argv=None):
    files = [files for root, dirs, files in os.walk(raw_dir)][0] # skip dirs as they are empty
    files = [f for f in files if not f[0] == '.' and f.endswith('_k.tif')] # exclude hidden files and filenames not ending with "_k.tif"
    files = sorted(files)

    for file in files:
        base = ''
        raw_path = os.path.join(raw_dir, file)

        name_parts = file.split("_")
        part_count = len(name_parts)
        final_part = name_parts[part_count - 2]
        lowercase = [c for c in final_part if c.islower()]

        # complex 
        if len(lowercase) > 0 and file != 'ucm_li_2000_019b_k.tif' and file != 'ucm_li_AS031f_k.tif':
            if part_count == 4:
                base = '_'.join(name_parts[0:-1])[0:-1]
            else: 
                alpha = lowercase[0] # all are 1-character 
                if final_part.startswith(alpha):
                    base = '_'.join(name_parts[0:-2])
                else:
                    base = '_'.join(name_parts[0:-1])[0:-1]
            new_path = os.path.join(new_path_dir, "complex", base, file)

        elif file.startswith('ucm_li_AS309'):
            base = '_'.join(name_parts[0:-2])
            new_path = os.path.join(new_path_dir, "complex", base, file)

        # simple
        else:
            new_path = os.path.join(new_path_dir, "simple", file)


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
