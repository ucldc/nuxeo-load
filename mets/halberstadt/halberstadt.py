#!/usr/bin/env python
""" Update collection in Nuxeo """
import sys, os
from lxml import etree
import pprint
from pynux import utils

#metadata_dir = "/apps/content/raw_files/UCD/halberstadt/METS/"
metadata_dir = "/apps/content/metadata/UCD/halberstadt"
pp = pprint.PrettyPrinter()
nx = utils.Nuxeo()
nuxeo_limit = 24

def main(argv=None):
    
    files = [files for root, dirs, files in os.walk(metadata_dir)][0]

    for file in files:
        filepath = os.path.join(metadata_dir, file)
        
        print "\n##", filepath, "##"
        tree = etree.parse(filepath)
        root = tree.getroot()
        item_dict = xml_to_dict(root)
        #pp.pprint(item_dict)
     
        payload = {}
        imagefile = os.path.splitext(file)[0] + '.tif'
        imagefile = imagefile[:nuxeo_limit]
        payload['path'] = os.path.join('/asset-library/UCD/Halberstadt/', imagefile)
        payload['properties'] = item_dict
        #print payload['path']
        #pp.pprint(payload)        
        uid = nx.get_uid(payload['path'])
        print "uid:", uid
        nx.update_nuxeo_properties(payload, path=payload['path'])
        print 'updated:', payload['path']



def xml_to_dict(document):
    """ convert mets XML to Nuxeo-friendly python dict """
    properties = {}
    properties_raw = extract_properties(document) 
    properties = format_properties(properties_raw)
    return properties


def format_properties(properties_list):
    """ create a dict of properties formatted for loading into Nuxeo """
    properties = {}
    repeatables = ("ucldc_schema:collection", "ucldc_schema:campusunit", "ucldc_schema:subjecttopic", "ucldc_schema:contributor", "ucldc_schema:creator", "ucldc_schema:date", "ucldc_schema:formgenre", "ucldc_schema:localidentifier", "ucldc_schema:language", "ucldc_schema:place", "ucldc_schema:publisher", "ucldc_schema:relatedresource", "ucldc_schema:rightsholder")

    # Turns out that there is only one instance of each property for these objects in the mets metadata we received. So we can just format each property and don't have to worry about concatenating any values.
    for property in properties_list:
        name = property[0]
        values = property[1]
        if isinstance(values, str):
            # remove extraneous line breaks
            values = values.split('\n')
            values = [v.strip() for v in values]
            values = ' '.join(values)
            if name in repeatables:
                values = [values]
            properties[name] = values
        else:
            value_dict = {}
            for value_list in values:
                value_dict[value_list[0]] = value_list[1]
            if name in repeatables:
                values = [value_dict]
            properties[name] = values

    return properties


def extract_properties(document):
    """ extract a list of properties from the XML """
    properties_raw = []
    nsmap = {'mets': 'http://www.loc.gov/METS/', 'mods': 'http://www.loc.gov/mods/v3', 'rts': 'http://cosimo.stanford.edu/sdr/metsrights/'}

    # ARK 
    objid = document.get('OBJID')
    properties_raw.append(['ucldc_schema:identifier', objid]) 

    # type
    type = document.get('TYPE')
    properties_raw.append(['ucldc_schema:type', type]) 
 
    # get metadata from MODS
    for mods in document.iterfind('mets:dmdSec/mets:mdWrap/mets:xmlData/mods:mods', namespaces=nsmap):
        # title
        for title in mods.iterfind('mods:titleInfo/mods:title', namespaces=nsmap):
            properties_raw.append(['dc:title', title.text])
        # creator
        for name in mods.iterfind('mods:name', namespaces=nsmap):
            for roleTerm in name.iterfind('mods:role/mods:roleTerm', namespaces=nsmap):
                if roleTerm.get('type') == 'text':
                    role = roleTerm.text
            lastname = ''
            firstname = ''
            for namePart in name.iterfind('mods:namePart', namespaces=nsmap):
                if namePart.get('type') == 'family':
                    lastname = namePart.text
                elif namePart.get('type') == 'given':
                    firstname = namePart.text
            fullname = ', '.join([lastname, firstname])
            creator_properties = []
            creator_properties.append(['role', role])
            creator_properties.append(['nametype', 'persname']) # all personal 
            creator_properties.append(['name', fullname])
            properties_raw.append(['ucldc_schema:creator', creator_properties])
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
        # formgenre FIXME
        for form in mods.iterfind('mods:relatedItem/mods:physicalDescription/mods:form', namespaces=nsmap):
            properties_raw.append(['ucldc_schema:formgenre', [['heading', form.text]]])
        # physical description 
        for physDesc in mods.iterfind('mods:relatedItem/mods:physicalDescription/mods:extent', namespaces=nsmap):
            properties_raw.append(['ucldc_schema:physdesc', physDesc.text])
        # access condition - to be used as part of rightstatement
        rightsnote_parts = [] 
        for access_condition in mods.iterfind('mods:accessCondition', namespaces=nsmap):
            rightsnote_parts.append(access_condition.text)

    # rights
    for rightsMD in document.iterfind('mets:amdSec/mets:rightsMD/mets:mdWrap/mets:xmlData/rts:RightsDeclarationMD', namespaces=nsmap):
        # rightsnote
        for rightsNote in rightsMD.iterfind('rts:Context/rts:Constraints/rts:ConstraintDescription', namespaces=nsmap):
            rightsnote_parts.append(rightsNote.text)
            rightsnote = ' '.join(rightsnote_parts)
            properties_raw.append(['ucldc_schema:rightsnote', rightsnote]) 

        for rightsDeclaration in rightsMD.iterfind('rts:RightsDeclaration', namespaces=nsmap):
            # rights status
            rightsCategory = rightsDeclaration.getparent().get('RIGHTSCATEGORY').lower()
            properties_raw.append(['ucldc_schema:rightsstatus', rightsCategory])
            # rights statement
            properties_raw.append(['ucldc_schema:rightsstatement', rightsDeclaration.text])
        # rights holder
        for rightsHolderName in rightsMD.iterfind('rts:RightsHolder/rts:RightsHolderName', namespaces=nsmap):
            properties_raw.append(['ucldc_schema:rightsholder', [['nametype', 'corpname'], ['name', rightsHolderName.text]]])
        # rights contact
        for rights_contact in rightsMD.iterfind('rts:RightsHolder/rts:RightsHolderContact', namespaces=nsmap):
            contact_parts = []
            for address in rights_contact.iterfind('rts:RightsHolderContactAddress', namespaces=nsmap):
                contact_parts.append(address.text)
         
            for phone in rights_contact.iterfind('rts:RightsHolderContactPhone', namespaces=nsmap):
                contact_parts.append(phone.text)
            for email in rights_contact.iterfind('rts:RightsHolderContactEmail', namespaces=nsmap):
                contact_parts.append(email.text)
            pp.pprint(contact_parts)
            contact = '. '.join(contact_parts)
            print "contact:", contact 
            properties_raw.append(['ucldc_schema:rightscontact', contact])
          
    # campusunit
    properties_raw.append(['ucldc_schema:campusunit', 'https://registry.cdlib.org/api/v1/repository/12/'])
    # collection
    properties_raw.append(['ucldc_schema:collection', 'https://registry.cdlib.org/api/v1/collection/2/'])

    return properties_raw 



if __name__ == "__main__":
    sys.exit(main())
