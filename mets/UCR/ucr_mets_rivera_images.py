__author__ = 'chris'

""" Update collection in Nuxeo """

import sys, os
import pprint
import csv

from lxml import etree
from pynux import utils

metadata_dir = "/apps/content/dsc_mets/9c2e65e471a83a104c2720d21da95ec3"
#metadata_dir = "/apps/content/rescue/ucr/digitalassets.lib.berkeley.edu/calcultures/ucr/mets/"
#metadata_dir = "/apps/registry/nuxeo-load/mets/UCR/test"

pp = pprint.PrettyPrinter()
nx = utils.Nuxeo()
nuxeo_limit = 24

def trace(msg, level=1):
   if level >= 10:
      sys.stderr.write('')

def main(argv=None):
   trace('Starting in method main.\n')

   # seq = ('ucldc_schema:identifier', 'ucldc_schema:description', 'ucldc_schema:rightscontact', 'ucldc_schema:localidentifier', 'ucldc_schema:type', 'dc:title', 'ucldc_schema:language', 'ucldc_schema:collection', 'ucldc_schema:subjecttopic', 'ucldc_schema:campusunit', 'ucldc_schema:rightsstatement', 'ucldc_schema:place', 'ucldc_schema:rightsholder', 'ucldc_schema:rightsstatus')
   dictlist = []

   files = [files for root, dirs, files in os.walk(metadata_dir)][0]
   files = [file for file in files if file.endswith('.xml')]

   for file in files:
      filepath = os.path.join(metadata_dir, file)
      tree = etree.parse(filepath)
      root = tree.getroot()
      thiscollection = extract_collection(root)
      if thiscollection is not None:
          print "\n##", filepath, "##'"
          item_dict = xml_to_dict(root)
          dictlist.append(item_dict)
          payload = {}
          imagefile = file
          payload['path'] = os.path.join('/asset-library/UCOP/dsc_mets3/UCR/rivera3', imagefile)
          payload['properties'] = item_dict

          pp.pprint(payload)
          # FOR LOAD: uncomment the next and third line below to load on registry-stg.
          uid = nx.get_uid(payload['path'])
          print "uid:", uid
          nx.update_nuxeo_properties(payload, path=payload['path'])
          print 'updated:', payload['path']

# FOR LOAD: comment next 8 lines.
#          csvkeys = list(item_dict.keys())
#          with open('/Users/elayem/ucldc/mets/Test/Lee/lee.csv', 'wab') as output_file:
#              dict_writer = csv.DictWriter(output_file, csvkeys)
#              dict_writer.writeheader()
#              # Uncomment next three lines to create an output dict and print to standard output
#              for data in dictlist:
#                  dict_writer.writerow(data)
#          print dictlist

def xml_to_dict(document):
   """ convert mets XML to Nuxeo-friendly python dict """
   properties = {}
   properties_raw = extract_properties(document)
   properties = format_properties(properties_raw)
   return properties


def format_properties(properties_list):
   """ create a dict of properties formatted for loading into Nuxeo """
   trace(str(properties_list), 3)
   properties = {}
   repeatables = (
      "ucldc_schema:collection",
      "ucldc_schema:campusunit",
      "ucldc_schema:subjecttopic",
      "ucldc_schema:contributor",
      "ucldc_schema:creator",
      "ucldc_schema:description",
      "ucldc_schema:date",
      "ucldc_schema:formgenre",
      "ucldc_schema:localidentifier",
      "ucldc_schema:language",
      "ucldc_schema:place",
      "ucldc_schema:publisher",
      "ucldc_schema:relatedresource",
      "ucldc_schema:rightsholder")

   # Turns out that there is only one instance of each property for these objects in the mets metadata we received. So we can just format each property and don't have to worry about concatenating any values.
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
            if name in repeatables:
               values = [values]
            properties[name] = values
         elif isinstance(values, list):
            if isinstance(values[0], dict):
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

def extract_collection(document):
    """ extract the collection name so we only get huber """
    nsmap = {'mets': 'http://www.loc.gov/METS/',
        'mods': 'http://www.loc.gov/mods/v3',
        'rts': 'http://cosimo.stanford.edu/sdr/metsrights/'}
    METSDMDSECDMR1 = 'mets:dmdSec[@ID="DMR1"]/mets:mdRef'
    for metsdmr1label in document.iterfind(METSDMDSECDMR1, namespaces=nsmap):
        ucldccollection = 'x'
        collection_name = metsdmr1label.attrib['LABEL']
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
   # Huber: https://registry.cdlib.org/api/v1/collection/10422/
   # Charles Lee: https://registry.cdlib.org/api/v1/collection/88/
   # Lippincott: https://registry.cdlib.org/api/v1/collection/13109/
   METSDMDSECDMR1 = 'mets:dmdSec[@ID="DMR1"]/mets:mdRef'
   for metsdmr1label in document.iterfind(METSDMDSECDMR1, namespaces=nsmap):
       ucldccollection = 'x'
       collection_name = metsdmr1label.attrib['LABEL']
       trace(collection_name, 10)
       # for collection_name in metsdmr1label.attrib['LABEL']:
       if collection_name == 'Charles H. Lee Papers, bulk 1912-1955':
           ucldccollection = 'https://registry.cdlib.org/api/v1/collection/88/'
       if collection_name == 'Joseph Barlow Lippincott Papers, 1882-1942':
           ucldccollection = 'https://registry.cdlib.org/api/v1/collection/13109/'
       if collection_name == 'Walter L. Huber Photograph Collection, 1911-1953':
           ucldccollection = 'https://registry.cdlib.org/api/v1/collection/10422/'
       trace(ucldccollection, 10)
       collection_properties = ['ucldc_schema:collection', ucldccollection]
       properties_raw.append(collection_properties)
       trace(collection_properties, 10)

   # get metadata from MODS
   MODSMODS = 'mets:dmdSec/mets:mdWrap/mets:xmlData/mods:mods'
   for mods in document.iterfind(MODSMODS, namespaces=nsmap):

      # dc:title
      for title in mods.iterfind('mods:titleInfo/mods:title', namespaces=nsmap):
         properties_raw.append(['dc:title', title.text])

#      # ucldc_schema:extent !!! SKIP !!! NOT MAPPED, so should not have a value !!!
#      for extent in mods.iterfind('mods:physicalDescription/mods:extent', namespaces=nsmap):
#         properties_raw.append(['ucldc_schema:extent', extent.text])

      # ucldc_schema:creator
      creator_items = []
      creator_count = 0
      for name in mods.iterfind('mods:name[@type="personal"]', namespaces=nsmap):
         name_type = 'persname'
         authority_id = name.get("authority")

         trace(str(dir(name))+'\n')
         role_term = name.find('mods:role/mods:roleTerm[@type="text"]', namespaces=nsmap).text
         trace('roleTerm: %s\n' % role_term)

         full_name = None

         if role_term:
            name_part = name.find('mods:namePart', namespaces=nsmap)
            full_name = name_part.text

         if full_name:
            creator_count += 1
            creator_items.append({'nametype': name_type,
                                  'name': full_name,
                                  'role': role_term,
                                  'authorityid': authority_id})
            trace('creatorItem %d: %s\n' % (creator_count, creator_items))

      trace('creatorItems(ALL): %s\n' % creator_items, 3)
      trace('ucldc_schema:creator: %s\n' % creator_items, 3)

      properties_raw.append(['ucldc_schema:creator', creator_items])

      # ucldc_schema:type
      for type in mods.iterfind('mods:typeOfResource', namespaces=nsmap):
         resource_type = 'image' if type.text == 'still image' else type.text
         properties_raw.append(['ucldc_schema:type', resource_type])

#      # uclcd_schema:formgenre !!!SKIP!!!
#      formgenre_items = []
#      for formgenre in mods.iterfind('mods:genre', namespaces=nsmap):
#         heading = formgenre.text
#         formgenre_items.append({'heading': heading})
#
#      formgenre_items = ['ucldc_schema:formgenre', formgenre_items]
#      trace('formgenreItems: %s\n' % formgenre_items)
#      properties_raw.append(formgenre_items)

      # uclcd_schema:localidentifier
      local_id_properties = []
      for local_id in mods.iterfind('mods:identifier[@type="local"]', namespaces=nsmap):
         id_type = local_id.get('type')
      if len(local_id.text) > 0:
         properties_raw.append(['ucldc_schema:localidentifier',
                                local_id.text])

#      # ucldc_schema:physdescription
#      for physical_description in mods.iterfind('mods:physicalDescription/mods:note', namespaces=nsmap):
#         description_type = physical_description.get('type')
#         description_item = physical_description.text
#         #properties_raw.append(['ucldc_schema:description', [['item', description_item], ['type', description_type]]])

      # ucldc_schema:description
      descscope_item = []
      for descscope in mods.iterfind('mods:abstract', namespaces=nsmap):
         #description_items.append(['item', description.text])
         #description_items.append(['type', 'scopecontent'])
         descscopeitem = descscope.text
         descscopetype = 'scopecontent'
         descscope_item.append({'item': descscopeitem, 'type': descscopetype})

#      descdate_item = []
#      for descdate in mods.iterfind('mods:note', namespaces=nsmap):
#         descdateitem = descdate.text
#         descdatetype = 'date'
#         descdate_item.append({'item': descdateitem, 'type': descdatetype})

      desccons_item = []
      for desccons in mods.iterfind('mods:physicalDescription/mods:note', namespaces=nsmap):
         descconsitem = desccons.text
         descconstype = 'conservation'
         desccons_item.append({'item': descconsitem, 'type': descconstype})

#      description_items = ['ucldc_schema:description', descscope_item, descdate_item]
      description_items = ['ucldc_schema:description', descscope_item, desccons_item]
#      description_items = ['ucldc_schema:description', descscope_item]
      trace('descriptionItems: %s\n' % description_items)
      properties_raw.append(description_items)

      # uclcd_schema:subjecttopic
      topic_items = []
      for subject_topic in mods.iterfind('mods:subject/mods:topic', namespaces=nsmap):
         heading = subject_topic.text
         heading_type = 'topic'
         source = subject_topic.getparent().get("authority")
#         source = 'lctgm'
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

      # ucldc_schema:relatedresource
      rel_resources = []
#      for related_title in mods.iterfind('mods:relatedItem[@displayLabel="Metacollection"]/mods:titleInfo/mods:title',
#                                         namespaces=nsmap):
      for rel_resource in mods.iterfind('mods:identifier[@type="uri"]', namespaces=nsmap):
         #displayLabel = related_title.getparent().getparent().get('displayLabel')
         #if displayLabel == 'Metacollection':
         related_resources.append(['item', rel_resource.text])
         properties_raw.append(['ucldc_schema:relatedresource', related_resources])

      # rights
      for rights_md in document.iterfind('mets:amdSec/mets:rightsMD/mets:mdWrap/mets:xmlData/rts:RightsDeclarationMD', namespaces=nsmap):
         rights_category = rights_md.get("RIGHTSCATEGORY").lower()
         properties_raw.append(['ucldc_schema:rightsstatus', rights_category])

      # rights statement
      for rights_description in rights_md.iterfind('rts:Context/rts:Constraints/rts:ConstraintDescription',
                                                   namespaces=nsmap):
         properties_raw.append(['ucldc_schema:rightsstatement', rights_description.text])

      # rights holder
      for rights_holder_name in rights_md.iterfind('rts:RightsHolder/rts:RightsHolderName', namespaces=nsmap):
         properties_raw.append(
            ['ucldc_schema:rightsholder', [{'nametype': 'corpname', 'name': rights_holder_name.text}]])

      # rights contact
      for rights_contact in rights_md.iterfind(
            'rts:RightsHolder/rts:RightsHolderContact/rts:RightsHolderContactAddress',
            namespaces=nsmap):
         properties_raw.append(['ucldc_schema:rightscontact', rights_contact.text])


   # ucldc_schema:campusunit
   properties_raw.append(['ucldc_schema:campusunit', 'https://registry.cdlib.org/api/v1/repository/21/'])

   # collection
   # collection = 'https://registry.cdlib.org/api/v1/collection/10422/'
   # for collection_name in mods.iterfind('//mets:dmdSec [@ID="DMR1"]/mets:mdRef/@LABEL', namespaces=nsmap):
   #     if collection_name == 'Charles H. Lee Papers, bulk 1912-1955':
   #         collection = 'https://registry.cdlib.org/api/v1/collection/88/'
   #     if collection_name == 'Joseph Barlow Lippincott Papers, 1882-1942':
   #         collection = 'https://registry.cdlib.org/api/v1/collection/13109/'
   #     if collection_name == 'Walter L. Huber Photograph Collection, 1911-1953':
   #         collection = 'https://registry.cdlib.org/api/v1/collection/10422/'
   #
   # collection_properties = ['ucldc_schema:collection', [{'item':  collection}]]
   # properties_raw.append(collection_properties)
   # trace("Collection properties : %s\n" % collection_properties, 10)

   # language
   properties_raw.append(['ucldc_schema:language', [{'language': 'English', 'languagecode': 'eng'}]])

   return properties_raw

if __name__ == "__main__":
   sys.exit(main())
