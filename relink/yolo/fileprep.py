#!/usr/bin/env python
import sys, os, zipfile
from lxml import etree

""" Unzip Yolo Aerial Photos zip files from Merritt. Create hardlinks to the files we want to upload """

BASE1 = u"/apps/content/raw_files/UCD/yolo"
BASE2 = u"/apps/content/new_path/UCD/YoloCountyAerial"
BASE3 = u"/apps/content/metadata/UCD/yolo"

def main(argv=None):
    zips = [files for root, dirs, files in os.walk(BASE1)][0]
    zips = [z for z in zips if z.startswith('vf') and zipfile.is_zipfile(os.path.join(BASE1, z))]

    for z in zips:
      zippath = os.path.join(BASE1, z)
      objectdir = get_obj_dir(BASE1, z)
      unpack(zippath, objectdir)
      wd = get_working_dir(objectdir)
      link_object(wd)
      link_metadata(wd)


def unpack(zip, targetdir):
    _mkdir(targetdir)
    with zipfile.ZipFile(zip, "r") as z:
        z.extractall(targetdir)


def get_obj_dir(dir, file):
    base, ext = os.path.splitext(file)
    return os.path.join(dir, base)


def get_working_dir(parentdir):
    """ find sub directory containing object and metadata for given unzipped Merritt object """
    # find highest version folder. data is in store/v00X/full/producer
    storedir = os.path.join(parentdir, 'store')
    vdirs = [subdir for subdir in os.walk(storedir).next()[1] if subdir.startswith('v')]
    versions = [[int(dir[1:]), dir] for dir in vdirs]
    latest_version = max([v[0] for v in versions])
    vdir = [vlist[1] for vlist in versions if vlist[0] == latest_version][0]
    working_dir = os.path.join(storedir, vdir, 'full', 'producer')

    return working_dir


def link_object(dir):
    fromfile = os.path.join(dir, 'FID1A.tif') 
    id = get_object_id(dir)
    tofile = os.path.join(BASE2, id + '.tif')
    try:
        os.remove(tofile)
    except:
        pass
    link_file(fromfile, tofile)


def link_metadata(dir):
    fromfile = os.path.join(dir, 'mets.txt')
    id = get_object_id(dir)
    tofile = os.path.join(BASE3, id + '.mets.txt')
    try:
        os.remove(tofile)
    except:
        pass
    link_file(fromfile, tofile)


def link_file(fullpath_from, fullpath_to):
    print "link {} {}".format(fullpath_from, fullpath_to)
    _mkdir(os.path.dirname(fullpath_to))
    os.link(fullpath_from, fullpath_to)


def get_object_id(dir):
    dc = os.path.join(dir, 'mrt-dc.xml')
    tree = etree.parse(dc)
    root = tree.getroot()
    id = [title.text for title in root.findall('{http://purl.org/dc/elements/1.1/}title')][0]
    return id

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
