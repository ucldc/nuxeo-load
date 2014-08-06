#!/usr/bin/env python
""" Update collection in Nuxeo """
import sys, os, requests
from lxml import etree
import pprint
from pynux import utils
from urlparse import urlparse

""" Import metadata into Nuxeo for 696 Lee Institute for Japanese Art collection objects as described here: https://wiki.library.ucsf.edu/display/UCLDC/DAMS+Collections+-+Initial+Load#DAMSCollections-InitialLoad-UCMerced """

metadata_dir = "/apps/content/metadata/UCM/LIJA2/CDL"
pp = pprint.PrettyPrinter()
nx = utils.Nuxeo()
nsmap = {'mets': 'http://www.loc.gov/METS/', 'mods': 'http://www.loc.gov/mods/v3', 'rts': 'http://cosimo.stanford.edu/sdr/metsrights/'}
nuxeo_basepath = '/asset-library/UCM/LIJA2/'
nuxeo_limit = 24 
toolong = []


def main(argv=None):
    
    naans = [dirs for root, dirs, files in os.walk(metadata_dir)][0]
    for naan in naans:
        naan_dir = os.path.join(metadata_dir, naan)
        arks = [dirs for root, dirs, files in os.walk(naan_dir)][0]
        for ark in arks:
            filepath = os.path.join(metadata_dir, naan, ark, ark + '.mets.xml')
            process_object(filepath)

    print "\n\nPath components over Nuxeo length limit (" + str(nuxeo_limit) + "):"
    print "TOTAL:", len(toolong)
    for long in toolong:
        print long



def process_object(filepath):

    print "\n##", filepath, "##"

    tree = etree.parse(filepath)
    document = tree.getroot()

    # get the structure of the object
    struct = get_struct(document)

    # update parent objects
    parent = struct['parent']
    properties = get_properties(document, parent['label'], 1)
    payload = assemble_payload(parent['path'], properties)
    update_nuxeo(payload)

    # update child objects
    for child in parent['children']:
        properties = get_properties(document, child['label'], 0)
        payload = assemble_payload(child['path'], properties) 
        update_nuxeo(payload)

        # update grandchild objects
        for grandchild in child['grandchildren']:
            properties = get_properties(document, grandchild['label'], 0)
            payload = assemble_payload(grandchild['path'], properties)
            update_nuxeo(payload)



def update_nuxeo(payload):

    path = payload['path']
    print "Nuxeo Path:", path
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

    #nx.update_nuxeo_properties(payload, path=payload['path'])
    #print 'updated:', payload['path']


def get_struct(document):

    struct = {} 

    # PARENT 
    for parent in document.iterfind('mets:structMap/mets:div', namespaces=nsmap):
        parent_info = get_struct_element_info(parent, '', document)
        parent_path = parent_info['path']

        # CHILDREN
        children = []
        for child in parent.iterfind('mets:div', namespaces=nsmap):
            if child.get('LABEL'):
                child_info = get_struct_element_info(child, parent_path, document)
                child_path = child_info['path']

                # GRANDCHILDREN
                grandchildren = []
                for grandchild in child.iterfind('mets:div', namespaces=nsmap):
                    if grandchild.get('LABEL'):
                        grandchild_info = get_struct_element_info(grandchild, child_path, document)
                        grandchildren.append(grandchild_info)

                child_info['grandchildren'] = grandchildren

                children.append(child_info)

        parent_info['children'] = children

        struct['parent'] = parent_info

    return struct



def get_struct_element_info(struct_element, parent_path, document):
    """ assemble a dict containing data we want for a given mets:structMap/mets:div element """
    element_info = {}

    label, object_id, norm_object_id, raw_filename, raw_path, new_filename = get_component_info(struct_element, document)

    if new_filename:
        path = os.path.join(parent_path, new_filename)
    else:
        path = os.path.join(parent_path, norm_object_id)

    element_info = get_component_dict(label, object_id, norm_object_id, raw_filename, raw_path, new_filename, path)

    return element_info


def get_component_info(element, document):
    """ get basic info for a particular object component """
    label = element.get('LABEL')
    object_id = get_object_id(document, label)
    norm_object_id = get_normalized_object_id(object_id)
    raw_filename, raw_path = get_master_file(document, element)
    new_filename = get_new_filename(raw_filename)
    return label, object_id, norm_object_id, raw_filename, raw_path, new_filename
 


def get_new_filename(raw_filename):
    """ normalize and truncate filename """
    new_filename = raw_filename 

    # truncate
    if new_filename[:7].lower() == "ucm_li_":
        new_filename = new_filename[7:]

    # capitalize
    name, extension = os.path.splitext(new_filename)
    new_filename = ''.join([name.upper(), extension])

    # special case
    if new_filename == '2003_099_LARGE-GROUP_K.tif':
        new_filename = '2003_099_LG-GROUP_K.tif'

    return new_filename 


def get_normalized_object_id(object_id):
    """ normalize the object ID """
    new_id = ''

    # replace whitespace with '_'
    if object_id:
        new_id = "_".join(object_id.split())        
     
    # capitalize
    new_id = new_id.upper()

    return new_id



def get_has_children(mets_div):
    """ determine whether or not this component has any children """
    has_children = 0

    for kid in mets_div.iterfind('mets:div', namespaces=nsmap):
        if kid.get('LABEL'):
            has_children = 1
  
    return has_children



def get_is_complex(document):
    """ determine whether an object is complex or not """
    mods_count = 0
    for mods in document.iterfind('mets:dmdSec/mets:mdWrap/mets:xmlData/mods:mods', namespaces=nsmap):
        mods_count = mods_count + 1
    if mods_count > 1:
        is_complex = 1
    else:
        is_complex = 0

    return is_complex



def get_component_dict(label, object_id, norm_object_id, raw_filename, raw_path, new_filename, path):

    info = {}
    info['label'] = label
    info['object_id'] = object_id
    info['norm_object_id'] = norm_object_id
    info['raw_filename'] = raw_filename
    info['raw_path'] = raw_path
    info['new_filename'] = new_filename
    info['path'] = path

    return info 



def get_properties(document, label, is_parent):
    """ get properties (metadata) for adding to object component in Nuxeo """

    # get properties
    item_dict = {}
    mods = get_mods_element(document, label)
    if mods is not None:
        item_dict = xml_to_dict(mods)
    else:
        item_dict['dc:title'] = label
        
    # if main object, get extra properties
    if is_parent:
        # get rights info 
        rights_dict = get_rights_dict(document)
        item_dict = dict(item_dict.items() + rights_dict.items())
        # get identifier
        item_dict['ucldc_schema:identifier'] = get_main_objid(document)

    return item_dict 



def get_object_id(document, label):
    try:
        # get mods element
        mods = get_mods_element(document, label)
        object_id = get_localidentifier(mods)
    except:
        object_id = label # this just an organizational folder.
    return object_id




def get_mods_element(document, label):
    for mdwrap in document.iterfind('mets:dmdSec/mets:mdWrap', namespaces=nsmap):
        if mdwrap.get('LABEL') == label:
            mods = mdwrap.find('mets:xmlData/mods:mods', namespaces=nsmap)
            return mods



def get_localidentifier(mods):
    for identifier in mods.iterfind('mods:identifier', namespaces=nsmap):
        if identifier.get('type') == "local" and identifier.text:
            return identifier.text



def get_main_objid(document):
    return document.get('OBJID')




def get_master_file(document, mets_div):
    """ choose the master file for this component for import into Nuxeo. This is the raw_file info, with filename not yet truncated or upper-cased. """
    master_filename = ''
    master_path = ''
    files = {}

    # get list of files for this component
    for fptr in mets_div.iterfind('mets:div/mets:fptr', namespaces=nsmap):
        file_id = fptr.get('FILEID')
        dir, filename = get_raw_filename(document, file_id)
        size = os.path.getsize(os.path.join(dir, filename))
        files[filename] = os.path.join(dir, filename)

    # determine master file 
    substrings = ['_g.mov', '_k.tif', '.tif']
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
    content_dir = "/apps/content/raw_files/UCM/LIJA2/"

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



def xml_to_dict(document):
    """ convert mets XML to Nuxeo-friendly python dict """
    properties = {}
    properties_raw = extract_properties(document) 
    properties = format_properties(properties_raw)
    return properties


def get_rights_dict(document):
    properties = {}
    properties_raw = extract_rights_properties(document)
    properties = format_properties(properties_raw)
    return properties 


def format_properties(properties_list):
    """ format values per property """
    properties = {}

    repeatables = ("ucldc_schema:alternativetitle", "ucldc_schema:collection", "ucldc_schema:campusunit", "ucldc_schema:subjecttopic", "ucldc_schema:contributor", "ucldc_schema:creator", "ucldc_schema:date", "ucldc_schema:formgenre", "ucldc_schema:localidentifier", "ucldc_schema:language", "ucldc_schema:place", "ucldc_schema:publisher", "ucldc_schema:relatedresource", "ucldc_schema:rightsholder")

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
        # title
        titleCount = 0
        for title in mods.iterfind('mods:titleInfo/mods:title', namespaces=nsmap):
            if titleCount == 0:
                properties_raw.append(['dc:title', title.text])
            else:
                properties_raw.append(['ucldc_schema:alternativetitle', title.text])
            titleCount = titleCount + 1
        # creator
        for creatorName in mods.iterfind('mods:name', namespaces=nsmap):
            creator_properties = []
            # name
            nameParts = []
            for part in creatorName.iterfind('mods:namePart', namespaces=nsmap):
                nameParts.append(part.text)
            name = ', '.join(nameParts)
            creator_properties.append(['name', name])
            # name type
            nameType = creatorName.get('type')
            if nameType == 'personal':
                typeShort = 'persname'
            elif nameType == 'corporate':
                typeShort = 'corpname'
            creator_properties.append(['type', typeShort])
            # role
            roleTerm = creatorName.find('mods:role/mods:roleTerm', namespaces=nsmap)
            role = roleTerm.text
            creator_properties.append(['role', role])
            # source
            authority = creatorName.get('authority')
            if authority:
                creator_properties.append(['source', authority])
                properties_raw.append(['ucldc_schema:creator', creator_properties])
        # type
        properties_raw.append(['ucldc_schema:type', 'image'])
        # genre
        for genre in mods.iterfind('mods:genre', namespaces=nsmap):
            properties_raw.append(['ucldc_schema:formgenre', [['heading', genre.text]]])
        # place
        for place in mods.iterfind('mods:originInfo/mods:place/mods:placeTerm', namespaces=nsmap):
            properties_raw.append(['ucldc_schema:place', [['name', place.text]]])
        # date created
        date_properties = []
        for date in mods.iterfind('mods:originInfo/mods:dateCreated', namespaces=nsmap):
            if date.get('point') == 'start':
                date_properties.append(['inclusivestart', date.text])
            elif date.get('point') == 'end':
                date_properties.append(['inclusiveend', date.text])
            else:
                date_properties.append(['date', date.text])
        if len(date_properties) > 0:
            date_properties.append(['datetype', 'created'])
            properties_raw.append(['ucldc_schema:date', date_properties]) 
        # date issued
        for date in mods.iterfind('mods:originInfo/mods:dateIssued', namespaces=nsmap):
            date_properties = []   
            date_properties.append(['date', date.text])
            date_properties.append(['dateype', 'issued']) 
            properties_raw.append(['ucldc_schema:date',  date_properties]) 
        # language
        for languageTerm in mods.iterfind('mods:language/mods:languageTerm', namespaces=nsmap):
            if languageTerm.text == 'chi':
                language = 'Chinese'
            elif languageTerm.text == 'eng':
                language = 'English' 
            elif languageTerm.text == 'jav':
                language = 'Javanese' 
            elif languageTerm.text == 'jpn':
                language = 'Japanese' 
            properties_raw.append(['ucldc_schema:language', [['language', language], ['languagecode', languageTerm.text]]])
        # local identifier
        for identifier in mods.iterfind('mods:identifier', namespaces=nsmap):
            if identifier.get('type') == "local" and identifier.text:
                properties_raw.append(['ucldc_schema:localidentifier', identifier.text])
        # physical description 
        desc = ''
        for physDesc in mods.iterfind('mods:physicalDescription', namespaces=nsmap):
            descParts = [part.text for part in physDesc]
            desc = ' '.join(descParts) 
        if desc:
            properties_raw.append(['ucldc_schema:physdesc', desc])
        # geographic subject
        for place in mods.iterfind('mods:subject/mods:geographic', namespaces=nsmap):
            place_properties = []
            place_properties.append(['source', place.getparent().get('authority')])
            place_properties.append(['name', place.text])
            properties_raw.append(['ucldc_schema:place', place_properties])
        # biographical note???
        # subjecttopic
        for subjecttopic in mods.iterfind('mods:subject/mods:topic', namespaces=nsmap):
            properties_raw.append(['ucldc_schema:subjecttopic', [['heading', subjecttopic.text], ['headingtype', 'topic']]])
        # relatedItem - concatenate various values into Source field.
        desc_parts = []
        for related_item in mods.iterfind('mods:relatedItem', namespaces=nsmap):
            for related_title_info in related_item.iterfind('mods:titleInfo/mods:title', namespaces=nsmap):
                desc_parts.append(related_title_info.text.strip())
            for identifier in related_item.iterfind('mods:identifier', namespaces=nsmap):
                if (identifier.get('type') == 'local' or identifier.get('type') == 'uri') and identifier.text:
                    desc_parts.append(identifier.text.strip())
            for related_physloc in related_item.iterfind('mods:location/mods:physicalLocation', namespaces=nsmap):
                desc_parts.append(related_physloc.text.strip())
            for related_url in related_item.iterfind('mods:url', namespaces=nsmap):
                desc_parts.append(related_url.text.strip()) 
        properties_raw.append(['ucldc_schema:source', '. '.join(desc_parts)])
        # physical location
        for location in mods.iterfind('mods:location/mods:physicalLocation', namespaces=nsmap):
            properties_raw.append(['ucldc_schema:physlocation', location.text])
        # physical location URL?
        # source
        for source in mods.iterfind('mods:recordInfo/mods:recordContentSource', namespaces=nsmap):
            properties_raw.append(['ucldc_schema:source', source.text])

        return properties_raw

def extract_rights_properties(document):
    properties_raw = []

    # rights - one per object
    for rightsMD in document.iterfind('mets:amdSec/mets:rightsMD/mets:mdWrap/mets:xmlData/rts:RightsDeclarationMD', namespaces=nsmap):
        # rights status
        rightsCategory = rightsMD.get('RIGHTSCATEGORY')
        if rightsCategory == 'COPYRIGHTED':
            properties_raw.append(['ucldc_schema:rightsstatus', 'copyrighted'])
        elif rightsCategory == 'PUBLIC DOMAIN':
            properties_raw.append(['ucldc_schema:rightsstatus', 'publicdomain'])
        # rights holder
        for rightsHolderName in rightsMD.iterfind('rts:RightsHolder/rts:RightsHolderName', namespaces=nsmap):
            properties_raw.append(['ucldc_schema:rightsholder', [['nametype', 'corpname'], ['name', rightsHolderName.text]]])
        # rights contact
        for address in rightsMD.iterfind('rts:RightsHolder/rts:RightsHolderContact/rts:RightsHolderContactAddress', namespaces=nsmap):
                properties_raw.append(['ucldc_schema:rightscontact', address.text])
        # rights statement 
        for rightsNote in rightsMD.iterfind('rts:Context/rts:Constraints/rts:ConstraintDescription', namespaces=nsmap):
            properties_raw.append(['ucldc_schema:rightsstatement', rightsNote.text]) 

    properties_raw.append(['ucldc_schema:campusunit', 'https://registry.cdlib.org/api/v1/repository/18/'])
    properties_raw.append(['ucldc_schema:collection', 'https://registry.cdlib.org/api/v1/collection/65/'])

    return properties_raw 


def assemble_payload(folder, properties):
    payload = {}
    payload['path'] = os.path.join(nuxeo_basepath, folder)
    payload['properties'] = properties
    return payload

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
