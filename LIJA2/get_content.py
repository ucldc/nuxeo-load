#!/usr/bin/env python
""" Update collection in Nuxeo """
import sys, os, requests
from lxml import etree
from urlparse import urlparse
import pprint

""" grab 696 UCM LIJA content files from UCB server """

metadata_dir = "/apps/content/metadata/UCM/LIJA2/UCB"
content_dir = "/apps/content/raw_files/UCM/LIJA2/"
nsmap = {'mets': 'http://www.loc.gov/METS/', 'xlink': 'http://www.w3.org/1999/xlink', 'mods': 'http://www.loc.gov/mods/v3'}
pp = pprint.PrettyPrinter()

def main(argv=None):
    
    files = [files for root, dirs, files in os.walk(metadata_dir)][0]

    count = 0
    for file in files:
        filepath = os.path.join(metadata_dir, file)
        print "\n###", filepath, "###"

        tree = etree.parse(filepath)
        root = tree.getroot()
        urls = get_urls(root)
        count = count + len(urls)
        for url in urls:
            # get ark
            parsed_orig_url = urlparse(url)
            ark = parsed_orig_url.path.split('/ark:/')[1]
            # open request
            r = requests.get(url, allow_redirects=True)
            # get filename, destdir and path
            path, filename = os.path.split(urlparse(r.url).path) 
            bare_path = os.path.join(content_dir, filename)
            dest_dir = os.path.join(content_dir, ark)
            dest_path = os.path.join(dest_dir, filename)
            print dest_path
            # don't get the file if it already exists
            if os.path.isfile(dest_path):
                print "File already exists, not doing anything."
            elif os.path.isfile(bare_path):
                _mkdir(dest_dir)
                os.rename(bare_path, dest_path)
                print "Moved file from", bare_path, "to", dest_path
            else:
                _mkdir(dest_dir)
                with open(dest_path, 'wb') as fd:
                    fd.write(r.content)
                print "Grabbed file."

        # FIXME need to allow for multiple files per object. Get all file URLs from <mets:FLocat> and create a mapping from the metadata file to a list of its components.
        #url = get_url(root)
        #filename = get_filename(root)
        #if not os.path.isfile(content_dir + filename):
            #grabfile(url, filename, file)
    print count

def get_urls(document):
    urls = []
    for FLocat in document.iterfind('mets:fileSec/mets:fileGrp/mets:file/mets:FLocat', namespaces=nsmap):
        urls.append(FLocat.attrib['{http://www.w3.org/1999/xlink}href'])
    return urls
           

def get_urlOLD(document):
    url = ''
    for fileGrp in document.iterfind('mets:fileSec/mets:fileGrp', namespaces=nsmap):
        if fileGrp.get('USE') == "image/master": 
            for file in fileGrp.iterfind('mets:file', namespaces=nsmap):
                if file.get('ID') == "FID1":
                    for FLocat in file.iterfind('mets:FLocat', namespaces=nsmap):
                        url = FLocat.attrib['{http://www.w3.org/1999/xlink}href']
    return url

def get_filenameOLD(document):
    filename = ''        
    for identifier in document.iterfind('mets:dmdSec/mets:/dWrap/mets:xmlData/mods:mods/mods:identifier', namespaces=nsmap):
        if identifier.get('type') == "local" and identifier.text:
            localID = identifier.text
            filename = localID + '.tif'
    return filename

def grabfileOLD(url, filename, metadata):
    source = "http://preservationassets.lib.berkeley.edu/jpnprints/ucm/images/" + filename
    print "grabbing", source
    dest = content_dir + filename
    try:
        response = urllib2.urlopen(source)
        content = response.read()
        with open(dest, "wb") as tif:
            tif.write(content)  
    except urllib2.HTTPError, e:
        print 'We failed with error code - %s.' % e.code

def grabfile(url, filename, metadata):
    dest = content_dir + filename 
    print "grabbing", url, dest
    
    try:
        response = urllib2.urlopen(url)
        content = response.read()
        with open(dest, "wb") as tif:
            tif.write(content)
    except urllib2.HTTPError, e:
        print 'We failed with error code - %s.' % e.code


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
