__author__ = 'chris'

""" Update collection in Nuxeo """

import re
import sys, os
import pprint
from pprint import pprint as pp

from lxml import etree
from pynux import utils

metadata_dir = "/apps/content/dsc_mets/5d1e0ccc1411c472208d3dc458b99697"

nx = utils.Nuxeo()
nuxeo_limit = 24

def trace(msg, level=1):
   if level >= 10:
      sys.stderr.write('')

def main(argv=None):
   trace('Starting in method main.\n')

   # seq = ('ucldc_schema:identifier', 'ucldc_schema:description', 'ucldc_schema:rightscontact', 'ucldc_schema:localidentifier', 'ucldc_schema:type', 'dc:title', 'ucldc_schema:language', 'ucldc_schema:collection', 'ucldc_schema:subjecttopic', 'ucldc_schema:campusunit', 'ucldc_schema:rightsstatement', 'ucldc_schema:place', 'ucldc_schema:rightsholder', 'ucldc_schema:rightsstatus')

   files = [files for root, dirs, files in os.walk(metadata_dir)][0]

   for file in files:
      if file.endswith('.mets.xml'):
         filepath = os.path.join(metadata_dir, file)
         tree = etree.parse(filepath)
         root = tree.getroot()

         colldir = '/asset-library/UCOP/barbaratest/UCSF/MSS-2001-19'
   
         print "\n##", filepath, "##"
   
######## Load parent
         print "\n## Loading Parent ##"
         item_dict = xml_to_dict(root)
   
         # pp.pprint(item_dict)
   
         payload = {}
         imagefile = extract_fname(root)
         imagefile = imagefile[:nuxeo_limit]
         payload['path'] = os.path.join(colldir, imagefile)
         payload['properties'] = item_dict
   
         pp(payload)
   
         uid = nx.get_uid(payload['path'])
         print "uid:", uid
         nx.update_nuxeo_properties(payload, path=payload['path'])
         print "updated:", payload['path']
   
######## Load children
         print "\n## Loading Children ##"
         print('---')
         for filename, modsmods in root_to_child_loop(root):
             #   print(filename)
             #   print(etree.tostring(modsmods))
   
            item_dict_child = xml_to_dict_child(modsmods)
   
            payload_child = {}
            payload_child['path'] = os.path.join(colldir, imagefile, filename)
            payload_child['properties'] = item_dict_child
   
            pp(payload_child)
   
            uid_child = nx.get_uid(payload_child['path'])
            print "child uid:", uid_child
            nx.update_nuxeo_properties(payload_child, path=payload_child['path'])
            print "\n##", filename, "##"
            print "updated:", payload_child['path']
   
######## End Load

def root_to_child_loop(doc):
    nsmap = {
        'mets': 'http://www.loc.gov/METS/',
        'mods': 'http://www.loc.gov/mods/v3',
        'xlink': 'http://www.w3.org/1999/xlink',
    }
    children = doc.xpath('mets:structMap[1]/mets:div//mets:div[@DMDID][mets:div[@TYPE="archive image"]]', namespaces=nsmap)
    for d in children:
        metadata_id = d.xpath('@DMDID')
        file_id = d.xpath('mets:div[@TYPE="archive image"]/mets:fptr[1]/@FILEID', namespaces=nsmap)
        metadata_xpath = 'mets:dmdSec[@ID="{}"]/mets:mdWrap[@MDTYPE="MODS"]/mets:xmlData/mods:mods'.format(metadata_id[0])
        metadata_tree = doc.xpath(metadata_xpath, namespaces=nsmap)[0]
        file_xpath = '//mets:file[@ID="{}"]/mets:FLocat/@xlink:href'.format(file_id[0])
        file_href = os.path.basename(doc.xpath(file_xpath, namespaces=nsmap)[0])
        yield(file_href, metadata_tree)
    

def xml_to_dict(document):
   """ convert mets XML to Nuxeo-friendly python dict """
   properties = {}
   properties_raw = extract_properties(document)
   properties = format_properties(properties_raw)
   return properties

def xml_to_dict_child(document):
   """ convert mets XML to Nuxeo-friendly python dict """
   properties = {}
   properties_raw = extract_modsproperties2(document)
   properties = format_properties(properties_raw)
   return properties

def format_properties(properties_list):
   """ create a dict of properties formatted for loading into Nuxeo """
   trace(str(properties_list), 3)
   properties = {}
   ###simple
   simplerepeatables = (
      "ucldc_schema:alternativetitle",
      "ucldc_schema:campusunit",
      "ucldc_schema:collection",
      "ucldc_schema:localidentifier",
      "ucldc_schema:publisher",
      "ucldc_schema:provenance",
      "ucldc_schema:relatedresource")
   ###complex
   repeatables = (
      "ucldc_schema:contributor",
      "ucldc_schema:creator",
      "ucldc_schema:description",
      "ucldc_schema:date",
      "ucldc_schema:formgenre",
      "ucldc_schema:language",
      "ucldc_schema:place",
      "ucldc_schema:rightsholder",
      "ucldc_schema:subjecttopic")

   ### Turns out that there is only one instance of each property for these objects in the mets metadata we received. So we can just format each property and don't have to worry about concatenating any values.
   for property in properties_list:
      name = property[0]
      values = property[1]
      trace('Formatting: %s -> %s\n' % (name, values), 5)

      if values:
         if isinstance(values, str) or isinstance(values, unicode):
            # remove extraneous line breaks
            values = values.split('\n')
            values = [v.strip() for v in values]
            values = ' '.join(values)
            if (name in simplerepeatables) or (name in repeatables):
               values = [values]
            properties[name] = values
         elif isinstance(values, list):
            if name in simplerepeatables:
               properties[name] = values
            elif isinstance(values[0], dict):
               properties[name] = values
            else:
               value_dict = {}
               for value_list in values:
                  trace( '>>>'+str(value_list)+'\n', 3)
                  value_dict[value_list[0]] = value_list[1]
               if name in repeatables:
                  values = [value_dict]
               properties[name] = values

   return properties

def extract_fname(document):
   """ extract the OBJID to get the image filename """
   nsmap = {'mets': 'http://www.loc.gov/METS/',
        'mods': 'http://www.loc.gov/mods/v3',
        'rts': 'http://cosimo.stanford.edu/sdr/metsrights/'}
   fname = document.get('OBJID')
   fname = fname.replace('ark:/13030/','') + '.mets.xml'
   return fname

def extract_collection(document):
   """ extract the collection name """
   nsmap = {'mets': 'http://www.loc.gov/METS/',
            'mods': 'http://www.loc.gov/mods/v3',
            'rts': 'http://cosimo.stanford.edu/sdr/metsrights/'}
   try:
      METSDMDSECDMR1 = document.find('mets:dmdSec[@ID="DMR1"]/mets:mdRef', namespaces=nsmap)
   except AttributeError as e:
      METSDMDSECDMR1 = False

   if METSDMDSECDMR1:
      collection_name = METSDMDSECDMR1.get('LABEL')
   else:
      collection_name = 'Unknown'

   return collection_name

def extract_properties(document):
   """ extract a list of properties from the XML """
   properties_raw = []
   nsmap = {'mets': 'http://www.loc.gov/METS/',
            'mods': 'http://www.loc.gov/mods/v3',
            'rts': 'http://cosimo.stanford.edu/sdr/metsrights/'}

   # ARK -- ucldc_schema:identifier
   objid = document.get('OBJID')
   properties_raw.append(['ucldc_schema:identifier', objid])

   # Collection -- ucldc_schema:collection
   for metsdmr1label in document.iterfind('mets:dmdSec[@ID="DMR1"]/mets:mdRef', namespaces=nsmap):
      ucldccollection = ''
      ucldccampusunit = ''
      collection_name = metsdmr1label.attrib['LABEL']
      trace(collection_name, 10)
      # Simple only collections
      if collection_name == 'Anne Frank photographs':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/48'
      if collection_name == 'Collection on Refugee Forums':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/53'
      if collection_name == 'Fort Chaffee photographs':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/45'
      if collection_name == 'Guire Cleary collection of Hmong and Iu Mien domestic artifacts':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/4567'
      if collection_name == 'Ly Kien Truc Photographs of the Hi-Tek Demonstrations':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/49'
      if collection_name == 'Van Le files on Southeast Asian refugees':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/12589'
      if collection_name == 'Orange County manuscript maps':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/16'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/59'
      # Complex and mixed collections
      if collection_name == 'Pleasants family papers':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/16'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/62'
      if collection_name == 'Mitsuye Yamada papers':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/16'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/25195'
      if collection_name == 'Orange County manuscript maps':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/16'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/59'
      if collection_name == 'Orange County Californio families portrait photograph album':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/16'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/60'
      if collection_name == 'Orange County rancho title abstracts':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/16'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/61'
      if collection_name == 'Paul Tran files on Southeast Asian refugees':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/57'
      if collection_name == 'Southeast Asia Resource Action Center records':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/54'
      if collection_name == 'Mitchell I. Bonner photographs and ephemera':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/44'
      if collection_name == 'Guire Cleary collection of Hmong and Iu Mien domestic artifacts':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/4567'
      if collection_name == 'Ly Kien Truc Photographs of the Hi-Tek Demonstrations':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/49'
      if collection_name == 'Van Le files on Southeast Asian refugees':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/12589'
      if collection_name == 'Brigitte Marshall collection on Southeast Asian refugees':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/50'
      if collection_name == 'Gayle Morrison files on Southeast Asian refugees':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/51'
      if collection_name == 'Project Ngoc records':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/52'
      if collection_name == 'Southeast Asian Genetics Program records':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/56'
      if collection_name == 'Collection on Refugee Forums':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/53'
      if collection_name == 'Southeast Asian Archive vertical file collection':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/55'
      if collection_name == 'Robert Walsh files on Southeast Asian refugee  resettlement and education':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/58'
      if collection_name == 'Linda Vo collection on the Southeast Asian American Experience archive project':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/23397'
      if collection_name == 'Fort Chaffee photographs':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/45'
      if collection_name == 'Anne Frank photographs':
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/48'
      if collection_name is None:
         ucldccampusunit = 'https://registry.cdlib.org/api/v1/repository/15'
         ucldccollection = 'https://registry.cdlib.org/api/v1/collection/42'

      trace(ucldccollection, 10)
      collection_properties = ['ucldc_schema:collection', ucldccollection]
      properties_raw.append(collection_properties)
      trace(collection_properties, 10)

      properties_raw.append(['ucldc_schema:campusunit', ucldccampusunit])

      # ucldc_schema:rightsstatus
      for rights_md in document.iterfind(
            'mets:amdSec/mets:rightsMD/mets:mdWrap/mets:xmlData/rts:RightsDeclarationMD', 
            namespaces=nsmap):
         rights_category = rights_md.get("RIGHTSCATEGORY").lower()
         properties_raw.append(['ucldc_schema:rightsstatus', rights_category])

      # ucldc_schema:rightsstatement
      for rights_description in rights_md.iterfind(
            'rts:Context/rts:Constraints/rts:ConstraintDescription', namespaces=nsmap):
         properties_raw.append(['ucldc_schema:rightsstatement', rights_description.text])

      # ucldc_schema:rightsholder
      for rights_holder_name in rights_md.iterfind(
            'rts:RightsHolder/rts:RightsHolderName', namespaces=nsmap):
         properties_raw.append(['ucldc_schema:rightsholder', 
                               [{'nametype': 'corpname', 'name': rights_holder_name.text}]])

      # ucldc_schema:rightscontact
      for rights_contact in rights_md.iterfind(
            'rts:RightsHolder/rts:RightsHolderContact/rts:RightsHolderContactAddress',
            namespaces=nsmap):
         properties_raw.append(['ucldc_schema:rightscontact', rights_contact.text])

   mods_properties = extract_modsproperties(document)
   properties_raw.extend(mods_properties)

   return properties_raw

def extract_modsproperties(document):
   """ extract a list of mods:mods properties from the XML """
   properties_raw = []
   nsmap = {'mets': 'http://www.loc.gov/METS/',
            'mods': 'http://www.loc.gov/mods/v3',
            'xlink': 'http://www.w3.org/1999/xlink',
            'rts': 'http://cosimo.stanford.edu/sdr/metsrights/'}

   ### get metadata from MODS
   #MODSMODS = 'mets:dmdSec/mets:mdWrap/mets:xmlData/mods:mods'
   #for mods in document.find(MODSMODS, namespaces=nsmap):

   try:
      mods = document.find('mets:dmdSec[@ID="DM1"]/mets:mdWrap/mets:xmlData/mods:mods', namespaces=nsmap)
   except AttributeError as e:
      mods = document.find('mods:mods', namespaces=nsmap)

   # dc:title
   for title in mods.iterfind('mods:titleInfo/mods:title', namespaces=nsmap):
      properties_raw.append(['dc:title', title.text])

   # ucldc_schema:extent
   for extent in mods.iterfind('mods:physicalDescription/mods:extent', namespaces=nsmap):
      properties_raw.append(['ucldc_schema:extent', extent.text])

   # ucldc_schema:creator
   creator_items = []
   for creator in mods.iterfind('mods:name', namespaces=nsmap):
      creator_name = creator.find('mods:namePart', namespaces=nsmap).text
      creator_type = creator.get("type")
      if creator_type == 'personal':
         name_type = 'persname'
      if creator_type == 'corporate':
         name_type = 'corpname'
      role_term = creator.find('mods:role/mods:roleTerm[@type="text"]', namespaces=nsmap).text
      authority_id = creator.get("authority")
      if authority_id is None:
         authority_id = ''

      creator_items.append({'nametype': creator_type,
                            'name': creator_name,
                            'role': role_term,
                            'authorityid': authority_id})

   creator_items = ['ucldc_schema:creator', creator_items]
   trace("creatorItems : %s\n" % creator_items, 3)
   properties_raw.append(creator_items)

   # ucldc_schema:type
   for type in mods.iterfind('mods:typeOfResource', namespaces=nsmap):
      #resource_type = 'image' if type.text == 'still image' else type.text
      if (type.text == 'still image') or (type.text == 'cartopgrahic'):
         resource_type = 'image'
      else:
         resource_type = type.text
      properties_raw.append(['ucldc_schema:type', resource_type])

   # ucldc_schema:formgenre
   formgenre_items = []
   for formgenre in mods.iterfind('mods:genre', namespaces=nsmap):
      formgenre_items.append({'heading': formgenre.text})

   formgenre_items = ['ucldc_schema:formgenre', formgenre_items]
   trace('formgenreItems: %s\n' % formgenre_items)
   properties_raw.append(formgenre_items)

   # ucldc_schema:date
   date_items = []
   datestart = ''
   dateend = ''
   try:
       date = mods.find('mods:originInfo/mods:dateCreated', namespaces=nsmap).text
   except AttributeError as e:
       date = False
   for startdate in mods.iterfind('mods:originInfo/mods:dateCreated[@point="start"]', namespaces=nsmap):
      datestart = startdate.text 
   for enddate in mods.iterfind('mods:originInfo/mods:dateCreated[@point="end"]', namespaces=nsmap):
      dateend = enddate.text 
   if date:
      datetype = "created"
      if datestart is None:
         datestart = ''
      if dateend is None:
         dateend = ''
      date_items.append({'date': date, 'datetype': datetype, 'inclusivestart': datestart, 'inclusiveend': dateend})
      date_items = ['ucldc_schema:date', date_items]
      trace('dateItems: %s\n' % date_items)

      properties_raw.append(date_items)

   # ucldc_schema:provenance
   provenance_items = []
   for provenance in mods.iterfind('mods:originInfo/mods:place/mods:placeTerm', namespaces=nsmap):
      provenance_items.append(provenance.text)
   properties_raw.append(['ucldc_schema:provenance', provenance_items])

   # ucldc_schema:publisher
   publisher_items = []
   for publisher in mods.iterfind('mods:originInfo/mods:publisher', namespaces=nsmap):
      publisher_items.append(publisher.text)
   properties_raw.append(['ucldc_schema:publisher', publisher_items])

   # ucldc_schema:localidentifier
   localid_items = []
   for localid in mods.iterfind('mods:identifier[@type="local"]', namespaces=nsmap):
      localid_items.append(localid.text)
   properties_raw.append(['ucldc_schema:localidentifier', localid_items])

   # ucldc_schema:physlocation
   for physlocation in mods.iterfind('mods:location/mods:physicalLocation', namespaces=nsmap):
      properties_raw.append(['ucldc_schema:physlocation', physlocation.text])

   # ucldc_schema:description
   desc_items = []
   for descnote in mods.iterfind('mods:note', namespaces=nsmap):
      descnote_item = descnote.text
      descnote_type = descnote.get('type')
      descnoteitem_type = 'scopecontent' if descnote_type == 'content' else 'marks'
      desc_items.append({'item': descnote_item, 'type': descnoteitem_type})

   for descscale in mods.iterfind('mods:subject/mods:cartographics/mods:scale', namespaces=nsmap):
      descscale_item = descscale.text
      descscaleitem_type = 'scopecontent'
      desc_items.append({'item': descscale_item, 'type': descscaleitem_type})

   description_items = ['ucldc_schema:description', desc_items]
   trace('descriptionItems: %s\n' % description_items)
   properties_raw.append(description_items)

   # ucldc_schema:subjectname
   subjectname_items = []
   for subject_name in mods.iterfind('mods:subject/mods:name/mods:namePart', namespaces=nsmap):
      subjectname = subject_name.text
      subjectname_items.append({'name': subjectname})

   subject_names = ['ucldc_schema:subjectname', subjectname_items]
   trace("subjectNames : %s\n" % subject_names, 5)
   properties_raw.append(subject_names)

   # ucldc_schema:subjecttopic
   topic_items = []
   for subject_topic in mods.iterfind('mods:subject/mods:topic', namespaces=nsmap):
      heading = subject_topic.text
      heading_type = 'topic'
      source = subject_topic.getparent().get("authority")
      if source is None:
         source = ''
      topic_items.append({'heading': heading,
                          'headingtype': heading_type,
                          'source': source})

   subject_topics = ['ucldc_schema:subjecttopic', topic_items]
   trace("subjectTopics : %s\n" % subject_topics, 5)
   properties_raw.append(subject_topics)

   # ucldc_schema:place
   place_items = []
   for place in mods.iterfind('mods:subject/mods:geographic', namespaces=nsmap):
      source = place.getparent().get("authority")
      name = place.text
      place_items.append({'source': source, 'name': name})

   place_items = ['ucldc_schema:place', place_items]
   trace("placeItems : %s\n" % place_items, 20)
   properties_raw.append(place_items)

   # ucldc_schema:language
   language_items = []
   for language in mods.iterfind('mods:language/mods:languageTerm', namespaces=nsmap):
      langcode = language.text
      lang = ''
      if langcode == 'cam':
         lang = 'Cambodian'
      if langcode == 'eng':
         lang = 'English'
      if langcode == 'hmo':
         lang = 'Hmong'
      if langcode == 'khm':
         lang = 'Khmer'
      if langcode == 'lao':
         lang = 'Lao'
      if langcode == 'vie':
         lang = 'Vietnamese'
      language_items.append({'language': lang, 'languagecode': langcode})

   languages = ['ucldc_schema:language', language_items]
   trace("Languages : %s\n" % languages, 5)
   properties_raw.append(languages)

   # ucldc_schema:relatedresource
   related_resources = []
   for related_title in mods.iterfind(
         'mods:relatedItem[@displayLabel="Metacollection"]/mods:titleInfo/mods:title', 
         namespaces=nsmap):
      related_resources.append(related_title.text)
   properties_raw.append(['ucldc_schema:relatedresource', related_resources])

   return properties_raw

def extract_modsproperties2(mods):
   """ extract a list of mods:mods properties from root_to_child_loop """
   properties_raw = []
   nsmap = {'mets': 'http://www.loc.gov/METS/',
            'mods': 'http://www.loc.gov/mods/v3',
            'xlink': 'http://www.w3.org/1999/xlink',
            'rts': 'http://cosimo.stanford.edu/sdr/metsrights/'}

   # dc:title
   title = mods.find('mods:titleInfo/mods:title', namespaces=nsmap)
   if title is not None:
      properties_raw.append(['dc:title', title.text])

   # ucldc_schema:alternativetitle
   alttitle_items = []
   for alttitle in  mods.iterfind('mods:titleInfo[@type="alternative"]/mods:title', namespaces=nsmap):
      alttitle_items.append(alttitle.text)
   properties_raw.append(['ucldc_schema:alternativetitle', alttitle_items])
      
   # ucldc_schema:type
   type = mods.find('mods:typeOfResource', namespaces=nsmap)
   if type is not None:
      if (type.text == 'still image') or (type.text == 'cartopgrahic'):
         resource_type = 'image'
      else:
         resource_type = type.text
      properties_raw.append(['ucldc_schema:type', resource_type])

   # ucldc_schema:formgenre
   formgenre_items = []
   for formgenre in mods.iterfind('mods:genre', namespaces=nsmap):
      formgenre_items.append({'heading': formgenre.text})

   formgenre_items = ['ucldc_schema:formgenre', formgenre_items]
   trace('formgenreItems: %s\n' % formgenre_items)
   properties_raw.append(formgenre_items)

   # ucldc_schema:localidentifier
   localid_items = []
   for localid in mods.iterfind('mods:identifier[@type="local"]', namespaces=nsmap):
      localid_items.append(localid.text)
   properties_raw.append(['ucldc_schema:localidentifier', localid_items])

   # ucldc_schema:physlocation
   physlocation = mods.find('mods:location/mods:physicalLocation', namespaces=nsmap)
   if physlocation is not None:
      properties_raw.append(['ucldc_schema:physlocation', physlocation.text])

   # ucldc_schema:description
   desc_items = []
   for descnote in mods.iterfind('mods:note', namespaces=nsmap):
      descnote_item = descnote.text
      descnote_type = descnote.get('type')
      descnoteitem_type = 'scopecontent' if descnote_type == 'content' else 'marks'
      desc_items.append({'item': descnote_item, 'type': descnoteitem_type})

   description_items = ['ucldc_schema:description', desc_items]
   trace('descriptionItems: %s\n' % description_items)
   properties_raw.append(description_items)

   # ucldc_schema:subjectname
   subjectname_items = []
   for subject_name in mods.iterfind('mods:subject/mods:name/mods:namePart', namespaces=nsmap):
      subjectname = subject_name.text
      subjectname_items.append({'name': subjectname})

   subject_names = ['ucldc_schema:subjectname', subjectname_items]
   trace("subjectNames : %s\n" % subject_names, 5)
   properties_raw.append(subject_names)

   # ucldc_schema:subjecttopic
   topic_items = []
   for subject_topic in mods.iterfind('mods:subject/mods:topic', namespaces=nsmap):
      heading = subject_topic.text
      heading_type = 'topic'
      source = subject_topic.getparent().get("authority")
      if source is None:
         source = ''
      topic_items.append({'heading': heading,
                          'headingtype': heading_type,
                          'source': source})

   subject_topics = ['ucldc_schema:subjecttopic', topic_items]
   trace("subjectTopics : %s\n" % subject_topics, 5)
   properties_raw.append(subject_topics)

   # ucldc_schema:place
   place_items = []
   for place in mods.iterfind('mods:subject/mods:geographic', namespaces=nsmap):
      source = place.getparent().get("authority")
      name = place.text
      place_items.append({'source': source, 'name': name})

   place_items = ['ucldc_schema:place', place_items]
   trace("placeItems : %s\n" % place_items, 20)
   properties_raw.append(place_items)

   # ucldc_schema:language
   language_items = []
   for language in mods.iterfind('mods:language/mods:languageTerm', namespaces=nsmap):
      langcode = language.text
      lang = ''
      if langcode == 'cam':
         lang = 'Cambodian'
      if langcode == 'eng':
         lang = 'English'
      if langcode == 'hmo':
         lang = 'Hmong'
      if langcode == 'khm':
         lang = 'Khmer'
      if langcode == 'lao':
         lang = 'Lao'
      if langcode == 'vie':
         lang = 'Vietnamese'
      language_items.append({'language': lang, 'languagecode': langcode})

   languages = ['ucldc_schema:language', language_items]
   trace("Languages : %s\n" % languages, 5)
   properties_raw.append(languages)

   return properties_raw

if __name__ == "__main__":
   sys.exit(main())
