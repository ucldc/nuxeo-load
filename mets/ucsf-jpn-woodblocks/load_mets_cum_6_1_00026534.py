#!/usr/bin/env python
""" Update collection in Nuxeo """
import sys, os, requests
from lxml import etree
import pprint
from pynux import utils
from urlparse import urlparse

metadata_dir = "/apps/content/metadata/UCSF/JapaneseWoodblocks/ucb_exceptions/"
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
    properties = get_properties(document, parent['label'], 1)
    objid = document.get('OBJID')
    properties['ucldc_schema:identifier'] = objid
    #pp.pprint(properties)
    payload = assemble_payload(parent['path'], properties)
    update_nuxeo(payload)

    # update child objects
    for child in parent['children']:
        properties = get_properties(document, child['label'], 0)
        #pp.pprint(properties)
        payload = assemble_payload(child['path'], properties)
        update_nuxeo(payload)    


def update_nuxeo(payload):

    path = payload['path']
    #pp.pprint(payload['properties'])

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



def get_properties(document, label, is_parent):
    """ get properties (metadata) for adding to object component in Nuxeo """

    # get properties
    item_dict = {}
    mods = get_mods_element(document, label)
    if mods is not None:
        item_dict = xml_to_dict(mods)
    else:
        item_dict['dc:title'] = label

    return item_dict



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
    #raw_filename, raw_path  = get_master_file(document, struct_element) 
    raw_filename = 'cum_6_1_00326037a_k.jpg'
    raw_path = '/apps/content/raw_files/UCSF/JapaneseWoodblocks/28722/bk000385230'
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
    parsed_url = urlparse(ucb_url)
    ark = parsed_url.path.split('/ark:/')[1]
    dir = os.path.join(content_dir, ark)
    try:
        filename = [files for root, dirs, files in os.walk(dir)][0][0]
    except:
        r = requests.get(ucb_url, allow_redirects=True)
        path, filename = os.path.split(urlparse(r.url).path)
        dest_dir = os.path.join(content_dir, ark)
        dest_path = os.path.join(dest_dir, filename)
        _mkdir(dest_dir)
        with open(dest_path, 'wb') as fd:
            fd.write(r.content)
            print "Grabbed file:", filename

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

def xml_to_dict(mods):
    """ convert mods XML to Nuxeo-friendly python dict """
    properties = {}
    properties_raw = extract_properties(mods) 
    properties = format_properties(properties_raw)
    return properties


def format_properties(properties_list):
    """ format values per property """
    properties = {}

    repeatables = ("ucldc_schema:alternativetitle", "ucldc_schema:collection", "ucldc_schema:campusunit", "ucldc_schema:subjecttopic", "ucldc_schema:contributor", "ucldc_schema:creator", "ucldc_schema:date", "ucldc_schema:formgenre", "ucldc_schema:localidentifier", "ucldc_schema:language", "ucldc_schema:place", "ucldc_schema:relatedresource", "ucldc_schema:rightsholder", "ucldc_schema:subjectname", "ucldc_schema:publisher")

    # get list of unique property names
    property_names = [p[0] for p in properties_list]
    property_names_set = set(property_names)
    property_names_unique = list(property_names_set)

    # aggregate and format values for each property name
    for name in property_names_unique:
        property_values = []
        formatted_property = {}
        # aggregate
        for sublist in properties_list:
            if sublist[0] == name:
                property_values.append(sublist[1])
        # format
        if name in repeatables:
            formatted_value = []
            for values in property_values:
                formatted_value.append(get_formatted_value(values))
        else:
            formatted_value = '. '.join(property_values)
        # put it all together
        formatted_property[name] = formatted_value
        properties.update(formatted_property)

    return properties


def get_formatted_value(values):
    """ format values for nuxeo. values can be string or list. convert lists to dicts. probably could've just captured this data as a dict in the first place! """
    if isinstance(values, list):
        value_dict = {}
        for item in values:
            value_dict[item[0]] = item[1]
        formatted = value_dict
    else:
        formatted = values

    return formatted


def extract_properties(mods):
    """ extract a list of properties from the XML """
    properties_raw = []

    # type
    properties_raw.append(['ucldc_schema:type', 'image']) 
    # campusunit
    properties_raw.append(['ucldc_schema:campusunit', 'https://registry.cdlib.org/api/v1/repository/25/'])
    # collection
    properties_raw.append(['ucldc_schema:collection', 'https://registry.cdlib.org/api/v1/collection/108/'])

    # get metadata from MODS
    # title
    for title_info in mods.iterfind('mods:titleInfo', namespaces=nsmap):
        if title_info.get('type') == 'alternative':
            for title in title_info.iterfind('mods:title', namespaces=nsmap):
                properties_raw.append(['ucldc_schema:alternativetitle', title.text])
        else:
            for title in title_info.iterfind('mods:title', namespaces=nsmap):
                properties_raw.append(['dc:title', title.text])
    # creator
    for name in mods.iterfind('mods:name', namespaces=nsmap):
        for roleTerm in name.iterfind('mods:role/mods:roleTerm', namespaces=nsmap):
            if roleTerm.get('type') == 'text':
                role = roleTerm.text
        for namePart in name.iterfind('mods:namePart', namespaces=nsmap):
            name_text = namePart.text
        creator_properties = []
        creator_properties.append(['role', role])
        creator_properties.append(['nametype', 'persname']) # all personal
        creator_properties.append(['name', name_text])
        properties_raw.append(['ucldc_schema:creator', creator_properties])
    # place
    for place_term in mods.iterfind('mods:originInfo/mods:place/mods:placeTerm', namespaces=nsmap):
        place = place_term.text
        properties_raw.append(['ucldc_schema:publisher', place]) 
    # date created
    date_properties = []
    for date in mods.iterfind('mods:originInfo/mods:dateCreated', namespaces=nsmap):
        if len(date.attrib) == 0:
            date_properties.append(['date', date.text])
        elif date.get('keyDate') == 'yes':
            date_properties.append(['single', date.text])
    if len(date_properties) > 0:
        date_properties.append(['datetype', 'created'])
        properties_raw.append(['ucldc_schema:date',  date_properties])        
    # form/genre
    for genre in mods.iterfind('mods:genre', namespaces=nsmap):
        source = genre.get('authority')
        properties_raw.append(['ucldc_schema:formgenre', [['heading', genre.text], ['source', source]]])
    # language
    for language_term in mods.iterfind('mods:language/mods:languageTerm', namespaces=nsmap):
        language_code = language_term.text
        if language_code == 'jpn':
            language = 'Japanese'
        elif language_code == 'eng':
            language = 'English'
        elif language_code == 'chi':
            language = 'Chinese'
        language_properties = []
        language_properties.append(['language', language]) 
        language_properties.append(['languagecode', language_code])
        properties_raw.append(['ucldc_schema:language', language_properties])
    # physical description
    for physDesc in mods.iterfind('mods:physicalDescription/mods:extent', namespaces=nsmap):
        properties_raw.append(['ucldc_schema:physdesc', physDesc.text])
    # description 
    for abstract in mods.iterfind('mods:abstract', namespaces=nsmap):
        properties_raw.append(['ucldc_schema:description', abstract.text])
    # subject
    for subject in mods.iterfind('mods:subject', namespaces=nsmap):
        subject_source = subject.get('authority')
        # topic
        for topic in subject.iterfind('mods:topic', namespaces=nsmap):
            topic_heading = topic.text
            properties_raw.append(['ucldc_schema:subjecttopic', [['heading', topic.text], ['headingtype', 'topic'], ['source', subject_source]]])
        # name
        for subjectname in subject.iterfind('mods:name', namespaces=nsmap):
            for name_part in subjectname.iterfind('mods:namePart', namespaces=nsmap):
                name = name_part.text
                if subjectname.get('type') == 'personal':
                    nametype = 'persname'
                elif subjectname.get('type') == 'corporate':
                    nametype = 'corpname'
                name_source = subjectname.get('authority') 
                name_properties = []
                name_properties.append(['name', name])
                name_properties.append(['nametype', nametype])
                name_properties.append(['source', name_source])
                #properties_raw.append(['ucldc_schema:subjectname', name_properties]) 
        # places
        for geographic in subject.iterfind('mods:geographic', namespaces=nsmap):
            place = geographic.text
            geo_properties = []
            geo_properties.append(['name', place]) 
            geo_properties.append(['source', subject_source])
            properties_raw.append(['ucldc_schema:place', geo_properties])
    
    # rights status
    properties_raw.append(['ucldc_schema:rightsstatus', 'copyrighted'])
    # rights statement
    properties_raw.append(['ucldc_schema:rightsstatement', 'Transmission or reproduction of materials protected by copyright beyond that allowed by fair use requires the written permission of the copyright owners. Works not in the public domain cannot be commercially exploited without permission of the copyright owner. Responsibility for any use rests exclusively with the user.'])

    return properties_raw 


if __name__ == "__main__":
    sys.exit(main())
