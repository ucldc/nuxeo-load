#!/usr/bin/env python
""" Update collection in Nuxeo """
import sys, os, requests
from lxml import etree
import pprint
from pynux import utils
from urlparse import urlparse

metadata_dir = "/apps/content/metadata/UCSF/JapaneseWoodblocks/ucb/"
pp = pprint.PrettyPrinter()
nx = utils.Nuxeo()
nuxeo_limit = 24
nuxeo_basepath = '/asset-library/UCSF/JapaneseWoodblocks'
nsmap = {'mets': 'http://www.loc.gov/METS/', 'mods': 'http://www.loc.gov/mods/v3', 'rts': 'http://cosimo.stanford.edu/sdr/metsrights/'}
toolong = []

def main(argv=None):
    
    files = [files for root, dirs, files in os.walk(metadata_dir)][0]

    complex_count = 0
    for file in files:
        filepath = os.path.join(metadata_dir, file)
        doc_id = file.split('.')[0]
        process_object(filepath, doc_id)


def process_object(filepath, doc_id):
 
    print "\n##", filepath, "##"

    tree = etree.parse(filepath)
    document = tree.getroot()

    struct = get_struct(document, doc_id)

    parent = struct['parent']
    properties = {}
    mods = get_mods_element(document, parent['label'])
    localid = mods.xpath('mods:identifier[@type="local"]/text()', namespaces=nsmap)[0]
    properties['ucldc_schema:localidentifier'] = [ localid ]
    #pp.pprint(properties)
    payload = assemble_payload(parent['path'], properties)
    update_nuxeo(payload)

    # update child objects
    for child in parent['children']:
        properties = {}
        mods = get_mods_element(document, child['label'])
        localid = mods.xpath('mods:identifier[@type="local"]/text()', namespaces=nsmap)[0]
        print(localid)
        properties['ucldc_schema:localidentifier'] = [ localid ]
        #pp.pprint(properties)
        payload = assemble_payload(child['path'], properties)
        update_nuxeo(payload)    


def update_nuxeo(payload):
    path = payload['path']
    pp.pprint(payload['properties'])

    # are any path parts too long? if so, capture that info so we can fix it b/c it'll cause problems.
    path_parts = path.split('/')
    toolong.extend([part for part in path_parts if len(part) > nuxeo_limit and part not in toolong])

    try:
        uid = nx.get_uid(path) # this will fail if object doesn't exist in nuxeo
        print "uid:", uid
        nx.update_nuxeo_properties(payload, path=payload['path'])
        print 'updated:', payload['path']
    except:
        print "uid: not in nuxeo"
        print "path:", path


def assemble_payload(folder, properties):
    payload = {}
    payload['path'] = os.path.join(nuxeo_basepath, folder)
    payload['properties'] = properties
    return payload


def get_mods_element(document, label):
    for mdwrap in document.iterfind('mets:dmdSec/mets:mdWrap', namespaces=nsmap):
        if mdwrap.get('LABEL') == label:
            mods = mdwrap.find('mets:xmlData/mods:mods', namespaces=nsmap)
            return mods


def get_struct(document, doc_id):

    struct = {}

    # PARENT
    for parent in document.iterfind('mets:structMap/mets:div', namespaces=nsmap):
        parent_info = get_struct_element_info(parent, '', document, doc_id)
        parent_path = parent_info['path'] 

        # CHILDREN
        children = []
        for child in parent.iterfind('mets:div', namespaces=nsmap):
            child_info = get_struct_element_info(child, parent_path, document, doc_id)

            children.append(child_info)

        parent_info['children'] = children

        struct['parent'] = parent_info

    return struct


def get_struct_element_info(struct_element, parent_path, document, doc_id):
    """ assemble a dict containing data we want for a given mets:structMap/mets:div element """
    element_info = {}

    # label
    label = struct_element.get('LABEL')
    element_info['label'] = label

    # raw filename and path
    raw_filename, raw_path  = get_master_file(document, struct_element) 
    element_info['raw_filename'] = raw_filename
    element_info['raw_path'] = raw_path

    # generic path
    if raw_filename:
        path = os.path.join(parent_path, raw_filename)
    else:
        path = os.path.join(parent_path, doc_id)

    element_info['path'] = path

    return element_info


def get_master_file(document, mets_div):
    """ choose the master file for this component for import into Nuxeo. This is the raw_file info, with filename not yet truncated or upper-cased. """
    master_filename = ''
    master_path = ''
    files = {}

    # get list of files for this component
    for fptr in mets_div.iterfind('mets:fptr', namespaces=nsmap):
        file_id = fptr.get('FILEID')
        dir, filename = get_raw_filename(document, file_id)
        #size = os.path.getsize(os.path.join(dir, filename))
        files[filename] = os.path.join(dir, filename)

    # determine master file
    substrings = ['.tif']
    for sub in substrings:
        if master_filename:
            break
        else:
            for key, value in files.iteritems():
                if sub in key:
                    master_filename = key
                    master_path = value

    return master_filename, master_path



def get_raw_filename(document, mets_file_id):
    """ given the FILEID from mets, find the name of the corresponding file we grabbed from UCB server """
    for metsfile in document.iterfind('mets:fileSec/mets:fileGrp/mets:file', namespaces=nsmap):
        if metsfile.get('ID') == mets_file_id:
            for flocat in metsfile.iterfind('mets:FLocat', namespaces=nsmap):
                if flocat.get('{http://www.w3.org/1999/xlink}href').startswith('http://nma.berkeley.edu'):
                    ucb_url = flocat.get('{http://www.w3.org/1999/xlink}href')
                    dir, filename = get_local_filepath(ucb_url)

    return dir, filename


def get_local_filepath(ucb_url):
    """ given UCB URL, get filepath of local file that we grabbed from UCB server """
    content_dir = "/apps/content/raw_files/UCSF/JapaneseWoodblocks/"

    # example: http://nma.berkeley.edu/ark:/28722/bk0000m7z5r
    real_url = ucb_url.replace('nma.berkeley.edu', 'vm172.lib.berkeley.edu:8080/resolver')
    parsed_url = urlparse(ucb_url)
    ark = parsed_url.path.split('/ark:/')[1]
    dir = os.path.join(content_dir, ark)
    try:
        # look in the local cache of ARK->filename
        filename = [files for root, dirs, files in os.walk(dir)][0][0]
    except:
        # do the lookup
        r = requests.head(real_url, allow_redirects=False)
        url_we_want = r.headers['Location']
        path, filename = os.path.split(urlparse(url_we_want).path)
        dest_dir = os.path.join(content_dir, ark)
        dest_path = os.path.join(dest_dir, filename)
        _mkdir(dest_dir)
        # just touch the files; no need to download
        # (in fact, some are fobidden from download)
        with open(dest_path, 'a'):  # http://stackoverflow.com/a/1160227/1763984
            os.utime(dest_path, None)
            print "Touched file:", filename
    return dir, filename

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
