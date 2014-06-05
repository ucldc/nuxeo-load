#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, pprint

""" Create hard links to UCSF Omeka files and group by collection. Link using shorter filenames than those provided by UCSF, as these are too long for Nuxeo """

BASE1 = u"/apps/content/raw_files/UCSF/omeka/omeka-files/files/"
BASE2 = u"/apps/content/raw_files/UCSF/omeka/omeka-fullsize/fullsize/"
BASE3 = u"/apps/content/new_path/UCSF/omeka/"
hardlinks_file = u"./hardlinks.txt"
missing_file = u"./missing.txt"

nuxeo_limit = 24

def main(argv=None):
    # get lists of files we have on the server
    rawfiles = [files for root, dirs, files in os.walk(BASE1)][0]
    rawfull = [files for root, dirs, files in os.walk(BASE2)][0]

    raw_listings = {
        'rawfiles' : rawfiles,
        'rawfull' : rawfull  
    }

    omeka_listings = [files for root, dirs, files in os.walk("./paths/")][0]

    try:
        os.remove(hardlinks_file)
    except OSError:
        pass

    try:
        os.remove(missing_file)
    except OSError:
        pass

    for collection in omeka_listings:
        with open(os.path.join("./paths/", collection)) as lf:
            print "\n## ", collection, " ##\n"
            process_collection(lf, raw_listings, collection)

def process_collection(filename_list, raw_listings, collection):
    missing = []
    linked = {}
    for filename in filename_list:
        filename = filename.rstrip('\n\r')
        rawpath = ''
        if filename in raw_listings['rawfiles']:
            rawpath = os.path.join(BASE1, filename)
        elif filename in raw_listings['rawfull']:
            rawpath = os.path.join(BASE2, filename)
        else:
            missing.append(filename)
 
        if rawpath: 
            if len(filename) > nuxeo_limit:
                shortname = shorten_filename(filename, nuxeo_limit)
            else:
                shortname = filename

            topath = os.path.join(BASE3, collection, shortname)
            link_file(rawpath, topath)
            linked[filename] = shortname 
    
    with open(hardlinks_file, "a+") as h:
        for k, v in linked.iteritems():
            h.write(' '.join([k,v]) + "\n")
 
    with open(missing_file, "a+") as f:
        f.write("\n## " + collection + " ##\n")
        for m in missing:
            f.write(m + '\n')


def link_file(fullpath_from, fullpath_to):
    print "link {} {}".format(fullpath_from, fullpath_to)
    _mkdir(os.path.dirname(fullpath_to))
    os.link(fullpath_from, fullpath_to)

def shorten_filename(filename, limit):
    shortname = ''
    parts = filename.split('.')
    base = parts[0]
    ext = parts[-1]
    base_parts = base.split('_')
    base_length = limit - len(ext) - 1
    # e.g.: speck_un2_weisz_1783_2561633c66.pdf
    if len(base_parts[-1]) == 10:
        checksum = base_parts[-1]
        del base_parts[-1]
        shortbase = '_'.join(base_parts)[:base_length - 11] 
        shortbase = shortbase.rstrip('_') + '_' + checksum
        shortname = '.'.join([shortbase, ext])
    # e.g.: 5be4b558b2db9592c02f.jpg
    elif len(base_parts) == 1 and len(base_parts[0]) == 32:
        shortbase = base_parts[0][:base_length]
        shortname = '.'.join([shortbase, ext])
    else:
        shortbase = base_parts[0][:base_length]
        shortname = '.'.join([shortbase, ext])

    return shortname


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
