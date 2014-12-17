#!/usr/bin/env python
""" Update collection in Nuxeo """
import sys, os
from lxml import etree
import pprint
from pynux import utils

#metadata_files = ["/apps/content/raw_files/UCM/nightingale/ucm_nightingale_1864.xml", "/apps/content/raw_files/UCM/nightingale/ucm_nightingale_1865.xml"]
metadata_files = []
metadata_files.append(["1864", "/apps/content/raw_files/UCM/nightingale/ucm_nightingale_1864.xml", "Image-Master-Edited"])
metadata_files.append(["1865", "/apps/content/raw_files/UCM/nightingale/ucm_nightingale_1865.xml", "Image-Master"])
pp = pprint.PrettyPrinter()
nx = utils.Nuxeo()
nuxeo_limit = 24
nsmap = {'mets': 'http://www.loc.gov/METS/', 'mods': 'http://www.loc.gov/mods/v3', 'rts': 'http://cosimo.stanford.edu/sdr/metsrights/'}

def main(argv=None):
    
    for mdfile in metadata_files:
        
        year = mdfile[0]
        filepath = mdfile[1]
        filetype = mdfile[2]

        print "\n##", filepath, "##"
        tree = etree.parse(filepath)
        document = tree.getroot()

        file_id_dict = get_fileid_dict(document)
        if year == '1864':
            metadata_dict = get_md_dict_1864(document)
        else:
            metadata_dict = get_md_dict_1865(document)

        #pp.pprint(metadata_dict)

        # iterate through objects describeed in the XML file and extract metadata
        for fileGrp in document.iterfind('mets:fileSec/mets:fileGrp', namespaces=nsmap):

            if fileGrp.get('USE') == filetype:

                for file in fileGrp.iterfind('mets:file', namespaces=nsmap):
                    # get properties
                    fileid = file.get('ID')
                    dmdid = file_id_dict[fileid]
                    title = metadata_dict[dmdid][0]
                    date = metadata_dict[dmdid][1]
                    description = metadata_dict[dmdid][2]
                    properties = {}
                    properties['dc:title'] = title
                    properties['ucldc_schema:date'] = [{'datetype': 'created', 'date': date}]
                    properties['ucldc_schema:transcription'] = description
                   
                    # get path 
                    url = ''
                    filename = ''
                    shortname = ''
                    for flocat in file.iterfind('mets:FLocat', namespaces=nsmap):
                        url = flocat.get('{http://www.w3.org/1999/xlink}href') 
                    filename = os.path.basename(url) 
                    if filename.startswith('Nightingale'):
                        shortname = filename.replace('Nightingale', 'ntgl')
                    elif filename.startswith('ucm_nightingale'):
                        shortname = filename.replace('ucm_nightingale', 'ntgl')
                    path = os.path.join('/asset-library/UCM/NightingaleDiaries', year, shortname) 

                    payload = {}
                    payload['path'] = path
                    payload['properties'] = properties
                    uid = nx.get_uid(payload['path'])
                    print "uid:", uid
                    nx.update_nuxeo_properties(payload, path=payload['path'])
                    print 'updated:', payload['path']


def get_fileid_dict(document):
    file_id_dict = {}
    for structMap in document.iterfind('mets:structMap', namespaces=nsmap):
        if structMap.get('TYPE') == 'logical':
            for label_div in structMap.iterfind('mets:div/mets:div', namespaces=nsmap):
                label = label_div.get('DMDID')
                file_ids = []
                for fptr in label_div.iterfind('mets:div/mets:fptr', namespaces=nsmap):
                    file_id_dict[fptr.get('FILEID')] = label

    return file_id_dict


def get_md_dict_1864(document):
    md_dict = {}
    for dmdSec in document.iterfind('mets:dmdSec', namespaces=nsmap):
        dm_id = ''
        title = ''
        date = ''
        description = ''
        dm_id = dmdSec.get('ID')
        for xml_data in dmdSec.iterfind('mets:mdWrap/mets:xmlData', namespaces=nsmap):
            for title in xml_data.iterfind('mets:title', namespaces=nsmap):
                title = title.text
            for date in xml_data.iterfind('mets:date', namespaces=nsmap):
                date = date.text
            for description in xml_data.iterfind('mets:description', namespaces=nsmap):
                description = description.text
        md_dict[dm_id] = [title, date, description]        

    return md_dict
 
def get_md_dict_1865(document):
    md_dict = {}
    for dmdSec in document.iterfind('mets:dmdSec', namespaces=nsmap):
        dm_id = ''
        title = ''
        date = ''
        transcription = ''
        dm_id = dmdSec.get('ID')
        for title in dmdSec.iterfind('mets:mdWrap/mets:xmlData/mods:mods/mods:titleInfo/mods:title', namespaces=nsmap):
            title = title.text
        for date_created in dmdSec.iterfind('mets:mdWrap/mets:xmlData/mods:mods/mods:originInfo/mods:dateCreated', namespaces=nsmap):
            date = date_created.text
        for note in dmdSec.iterfind('mets:mdWrap/mets:xmlData/mods:mods/mods:note', namespaces=nsmap):
            if note.get('displayLabel') == 'Transcription':
                transcription = note.text
        
        md_dict[dm_id] = [title, date, transcription]

    return md_dict



if __name__ == "__main__":
    sys.exit(main())
