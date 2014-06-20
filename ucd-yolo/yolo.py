#!/usr/bin/env python
""" Update collection in Nuxeo """
import sys, os
from lxml import etree
import pprint
from pynux import utils

metadata_dir = "/apps/content/metadata/UCD/yolo/"
pp = pprint.PrettyPrinter()
nx = utils.Nuxeo()

def main(argv=None):
    
    files = [files for root, dirs, files in os.walk(metadata_dir)][0]

    for file in files:
        filepath = os.path.join(metadata_dir, file)

        tree = etree.parse(filepath)
        root = tree.getroot()
        item_dict = xml_to_dict(root)
         
        payload = {}
        title = item_dict['dc:title']
        payload['path'] = os.path.join('/asset-library/UCD/YoloCountyAerial/', title + '.tif')
        payload['properties'] = item_dict
        #pp.pprint(payload)        
        uid = nx.get_uid(payload['path'])
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
    for mods in document.iterfind('mets:dmdSec/mets:mdWrap/mets:xmlData/mods:mods', namespaces=nsmap):
        # title
        for title in mods.iterfind('mods:titleInfo/mods:title', namespaces=nsmap):
            properties_raw.append(['dc:title', title.text])
        # creator
        for name in mods.iterfind('mods:name', namespaces=nsmap):
            roleTerm = name.find('mods:role/mods:roleTerm', namespaces=nsmap)
            role = roleTerm.text
            if role == 'creator':
                creator_properties = []
                creator_properties.append(['role', 'creator'])
                creator_properties.append(['source', roleTerm.get('authority')])
                creator_properties.append(['name', name.find('mods:namePart', namespaces=nsmap).text])
                properties_raw.append(['ucldc_schema:creator', creator_properties])
        # type
        properties_raw.append(['ucldc_schema:type', 'image'])
        # date issued
        for date in mods.iterfind('mods:originInfo/mods:dateIssued', namespaces=nsmap):
            date_properties = []   
            date_properties.append(['date', date.text])
            date_properties.append(['dateype', 'issued']) 
            properties_raw.append(['ucldc_schema:date',  date_properties]) 
        # language
        properties_raw.append(['ucldc_schema:language', [['language', 'English'], ['languagecode', 'eng']]])
        # local identifier
        for identifier in mods.iterfind('mods:identifier', namespaces=nsmap):
            if identifier.get('type') == "local" and identifier.text:
                properties_raw.append(['ucldc_schema:localidentifier', identifier.text])
        # physical description 
        for physDesc in mods.iterfind('mods:physicalDescription/mods:extent', namespaces=nsmap):
            properties_raw.append(['ucldc_schema:physdesc', physDesc.text])
        # places
        for place in mods.iterfind('mods:subject/mods:geographic', namespaces=nsmap):
            place_properties = []
            place_properties.append(['source', place.getparent().get('authority')])
            place_properties.append(['name', place.text])
            properties_raw.append(['ucldc_schema:place', place_properties])
        # physical location
        for location in mods.iterfind('mods:location/mods:physicalLocation', namespaces=nsmap):
            properties_raw.append(['ucldc_schema:physlocation', location.text])
        # source
        for source in mods.iterfind('mods:recordInfo/mods:recordContentSource', namespaces=nsmap):
            properties_raw.append(['ucldc_schema:source', source.text])

    # rights
    for rightsMD in document.iterfind('mets:amdSec/mets:rightsMD/mets:mdWrap/mets:xmlData/rts:RightsDeclarationMD', namespaces=nsmap):
        for rightsDeclaration in rightsMD.iterfind('rts:RightsDeclaration', namespaces=nsmap):
            # rights status
            rightsCategory = rightsDeclaration.getparent().get('RIGHTSCATEGORY').lower()
            properties_raw.append(['ucldc_schema:rightsstatus', rightsCategory])
            # rights statement
            properties_raw.append(['ucldc_schema:rightsstatement', rightsDeclaration.text])
        # rights holder
        for rightsHolder in rightsMD.iterfind('rts:RightsHolder/rts:RightsHolderName', namespaces=nsmap):
            properties_raw.append(['ucldc_schema:rightsholder', [['nametype', 'corpname'], ['name', rightsHolder.text]]])
        # rights note
        for rightsNote in rightsMD.iterfind('rts:Context/rts:Constraints/rts:ConstraintDescription', namespaces=nsmap):
            properties_raw.append(['ucldc_schema:rightsnote', rightsNote.text]) 

    properties_raw.append(['ucldc_schema:campusunit', 'https://registry.cdlib.org/api/v1/repository/12/'])
    properties_raw.append(['ucldc_schema:collection', 'https://registry.cdlib.org/api/v1/collection/5/'])

    return properties_raw 



if __name__ == "__main__":
    sys.exit(main())
