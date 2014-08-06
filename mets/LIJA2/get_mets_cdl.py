#!/usr/bin/env python
""" grab mets files from cdl dsc server """
import sys, os, pprint, requests
from lxml import etree

# /apps/dsc/data/xtf/data/13030/09/hb7s201209/hb7s201209.mets.xml
pp = pprint.PrettyPrinter()
ucb_dir = "/apps/content/metadata/UCM/LIJA2/UCB"
cdl_dir = "/apps/content/metadata/UCM/LIJA2/CDL"

def main():
    files = [files for root, dirs, files in os.walk(ucb_dir)][0]
    for file in files:
        filepath = os.path.join(ucb_dir, file)
        print "\n##", filepath, "##"

        tree = etree.parse(filepath)
        root = tree.getroot()
        # get dsc url to grab mets from
        fullark = root.get('OBJID')
        dsc_url = 'http://content.cdlib.org/mets/' + fullark + '/'
        print dsc_url
        # get destination path for writing mets to
        naanark = fullark.split('ark:/')[1]
        ark = naanark.split('/')[1]
        dest_dir = os.path.join(cdl_dir, naanark)
        dest_path = os.path.join(dest_dir, ark + '.mets.xml')
        print dest_path
        # open request
        r = requests.get(dsc_url)
        if os.path.isfile(dest_path):
            print "File already exists, not grabbing."
        else:
            _mkdir(dest_dir)
            with open(dest_path, 'wb') as fd:
                fd.write(r.content)
            print "Grabbed file." 




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



if __name__ == '__main__':
    main()
