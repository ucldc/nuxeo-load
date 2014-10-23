#!/usr/bin/env python
import sys, os
import pprint

""" Hardlink UCR Highlander Student Newspaper files for loading into Nuxeo """

raw_dir = u"/apps/content/raw_files/UCR/highlander student newspaper"
new_path_dir = u"/apps/content/new_path/UCR/HighlanderNewspaper"
pp = pprint.PrettyPrinter()

def main(argv=None):
    years = [dirs for root, dirs, files in os.walk(raw_dir)][0]
    for year in years:
        year_dir = os.path.join(raw_dir, year)
        pp.pprint(year_dir)
        # 2005-2006 has subdirectories (is complex)
        if year == '2005-2006':
            issues = [dirs for root, dirs, files in os.walk(year_dir)][0]
            for issue in issues:
                issue_dir = os.path.join(year_dir, issue) 
                issue_no_spaces = ''.join(issue.split(' '))
                files = [files for root, dirs, files in os.walk(issue_dir)][0]
                for file in files:
                    raw_path = os.path.join(issue_dir, file)
                    new_path = os.path.join(new_path_dir, year, issue_no_spaces, file)
                    link_file(raw_path, new_path)
        else:
            files = [files for root, dirs, files in os.walk(year_dir)][0]
            for file in files:
                raw_path = os.path.join(year_dir, file)
                new_path = os.path.join(new_path_dir, year, file)
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
