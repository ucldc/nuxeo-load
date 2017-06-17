__author__ = 'chris'

""" Update collection in Nuxeo """

import sys, os
import pprint
import csv

from lxml import etree
from pynux import utils

metadata_dir = "/home/lvoong/mets/uci/test"

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

   for file in files:
      filepath = os.path.join(metadata_dir, file)
      tree = etree.parse(filepath)
      root = tree.getroot()
      thiscollection = extract_collection(root)
      if thiscollection:
          if thiscollection == 'Anne Frank photographs':
              colldir = '/asset-library/UCOP/dsc_mets/UCI/MS-SEA032/'
          if thiscollection == 'Collection on Refugee Forums':
              colldir = '/asset-library/UCOP/dsc_mets/UCI/MS-SEA019/'
          if thiscollection == 'Fort Chaffee photographs':
              colldir = '/asset-library/UCOP/dsc_mets/UCI/MS-SEA025/'
          if thiscollection == 'Guire Cleary collection of Hmong and Iu Mien domestic artifacts':
              colldir = '/asset-library/UCOP/dsc_mets/UCI/MS-SEA008/'
          if thiscollection == 'Ly Kien Truc Photographs of the Hi-Tek Demonstrations':
              colldir = '/asset-library/UCOP/dsc_mets/UCI/MS-SEA010/'
          if thiscollection == 'Van Le files on Southeast Asian refugees':
              colldir = '/asset-library/UCOP/dsc_mets/UCI/MS-SEA012/'
          if thiscollection == 'Orange County manuscript maps':
              colldir = '/asset-library/UCOP/dsc_mets/UCI/MS-R072/'
          print "\n##", filepath, "##"
          print thiscollection
          item_dict = xml_to_dict(root)

          # pp.pprint(item_dict)
          dictlist.append(item_dict)
          payload = {}
          imagefile = extract_fname(root)
          #imagefile = os.path.splitext(file)[0] + '.jpg'
          imagefile = imagefile[:nuxeo_limit]
          payload['path'] = os.path.join(colldir, imagefile)
          payload['properties'] = item_dict

          print payload
# FOR LOAD: uncomment the next and third line below to load on registry-stg.
          uid = nx.get_uid(payload['path'])
          print "uid:", uid
          nx.update_nuxeo_properties(payload, path=payload['path'])
          print 'updated:', payload['path']

          #csvkeys = list(item_dict.keys())
          #with open('/home/lvoong/mets/uci/kt2f59q35j_mets.csv', 'wab') as output_file:
          #    dict_writer = csv.DictWriter(output_file, csvkeys)
          #    dict_writer.writeheader()
# FOR LOAD: comment next four lines.
          # Uncomment next three lines to create an output dict and print to standard output
          #    for data in dictlist:
          #        dict_writer.writerow(data)
          #print dictlist

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
         if isinstance(values, str):
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
    METSDMDSECDMR1 = 'mets:dmdSec[@ID="DMR1"]/mets:mdRef'
    for metsdmr1label in document.iterfind(METSDMDSECDMR1, namespaces=nsmap):
        #ucldccollection = 'x'
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
   METSDMDSECDMR1 = 'mets:dmdSec[@ID="DMR1"]/mets:mdRef'
   for metsdmr1label in document.iterfind(METSDMDSECDMR1, namespaces=nsmap):
       ucldccollection = ''
       collection_name = metsdmr1label.attrib['LABEL']
       trace(collection_name, 10)
#Collections:
#
# Simple    kt4p3021fr    Anne Frank photographs
# Simple    kt5s2013bp    Collection on Refugee Forums
# Simple    kt2f59q35j    Fort Chaffee photographs
# Simple    kt9v19q84     Guire Cleary collection of Hmong and Iu Mien domestic artifacts
# Simple    kt85801594    Ly Kien Truc Photographs of the Hi-Tek Demonstrations
# Simple    kt5h4nc8rn    Van Le files on Southeast Asian refugees
# Simple    tf9k4009f8    Orange County manuscript maps
#
# kt1h4nb6dt    Brigitte Marshall collection on Southeast Asian refugees
# kt6s2013d1    Gayle Morrison files on Southeast Asian refugees
# kt4h4nc7pt    Linda Vo collection on the Southeast Asian American Experience archive project
# kt996nd0d0    Mitchell I. Bonner photographs and ephemera
# tf5d5nb2wc    Mitsuye Yamada papers
# kt196nc419    Orange County Californio families portrait photograph album
# kt1m3nb7nk    Orange County rancho title abstracts
# tf8f59p1tg    Paul Tran files on Southeast Asian refugees
# tf967nb619    Pleasants family papers
# kt8z09p8pd    Project Ngoc records
# kt6v19p6sq    Robert Walsh files on Southeast Asian refugee  resettlement and education
# kt467nc6pc    Southeast Asia Resource Action Center records
# kt7j49q6qg    Southeast Asian Archive vertical file collection
# kt1h4nb6fb    Southeast Asian Genetics Program records
#
       if collection_name == 'Anne Frank Photographs':
           ucldccollection = 'https://registry.cdlib.org/api/v1/collection/48'
       if collection_name == 'Fort Chaffee photographs':
           ucldccollection = 'https://registry.cdlib.org/api/v1/collection/45'
       if collection_name == 'Guire Cleary collection of Hmong and Iu Mien domestic artifacts':
           ucldccollection = 'https://registry.cdlib.org/api/v1/collection/4567'
       if collection_name == 'Ly Kien Truc Photographs of the Hi-Tek Demonstrations':
           ucldccollection = 'https://registry.cdlib.org/api/v1/collection/49'
       if collection_name == 'Refugee Forums Collection':
           ucldccollection = 'https://registry.cdlib.org/api/v1/collection/53'
       if collection_name == 'Orange County manuscript maps':
           ucldccollection = 'https://registry.cdlib.org/api/v1/collection/59'
       if collection_name == 'Van Le files on Southeast Asian refugees':
           ucldccollection = 'https://registry.cdlib.org/api/v1/collection/12589'
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
         resource_type = 'image' if type.text == 'still image' else type.text
         properties_raw.append(['ucldc_schema:type', resource_type])

      # uclcd_schema:formgenre
      formgenre_items = []
      for formgenre in mods.iterfind('mods:genre', namespaces=nsmap):
         heading = formgenre.text
         formgenre_items.append({'heading': heading})

      formgenre_items = ['ucldc_schema:formgenre', formgenre_items]
      trace('formgenreItems: %s\n' % formgenre_items)
      properties_raw.append(formgenre_items)

      # uclcd_schema:date
      #date_items = []
      #for datecreated in mods.find('mods:originInfo/mods:dateCreated', namespaces=nsmap):
      #   date = datecreated.text
      #   datetype = "created"
      #   date_items.append({'date': date, 'datetype': datetype})

      date_items = []
      date = mods.find('mods:originInfo/mods:dateCreated', namespaces=nsmap).text
      if date:
         datetype = "created"
         date_items.append({'date': date, 'datetype': datetype})
         date_items = ['ucldc_schema:date', date_items]
         trace('dateItems: %s\n' % date_items)
         properties_raw.append(date_items)

      # uclcd_schema:localidentifier
      local_id_properties = []
      for local_id in mods.iterfind('mods:identifier[@type="local"]', namespaces=nsmap):
         id_type = local_id.get('type')
      if len(local_id.text) > 0:
         properties_raw.append(['ucldc_schema:localidentifier',
                                local_id.text])

      # ucldc_schema:physdescription
      #for physical_description in mods.iterfind('mods:physicalDescription/mods:note', namespaces=nsmap):
      #   description_type = physical_description.get('type')
      #   description_item = physical_description.text
      #   #properties_raw.append(['ucldc_schema:description', [['item', description_item], ['type', description_type]]])

      # ucldc_schema:physlocation
      for physlocation in mods.iterfind('mods:location/mods:physicalLocation', namespaces=nsmap):
         properties_raw.append(['ucldc_schema:physlocation', physlocation.text])

      # ucldc_schema:description
      descscope_item = []
      for descscope in mods.iterfind('mods:note', namespaces=nsmap):
         descscopeitem = descscope.text
         descscopetype = 'scopecontent'
         descscope_item.append({'item': descscopeitem, 'type': descscopetype})

      description_items = ['ucldc_schema:description', descscope_item]
      trace('descriptionItems: %s\n' % description_items)
      properties_raw.append(description_items)

      # uclcd_schema:subjectname
      #subjectname_items = []
      #for subject_name in mods.iterfind('mods:subject/mods:name/mods:namePart', namespaces=nsmap):
      #   subjectname = subject_name.text
      #   subjectname_items.append({'name': subjectname})

      #subject_names = ['ucldc_schema:subjectname', subjectname_items]
      #trace("subjectNames : %s\n" % subject_names, 5)
      #properties_raw.append(subject_names)

      # uclcd_schema:subjecttopic
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

      # languages
      #
      #cam - Cambodian
      #eng - English
      #hmo - Hmong
      #khm - Khmer
      #lao - Lao
      #vie - Vietnamese

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
      #for related_title in mods.iterfind('mods:relatedItem[@displayLabel="Metacollection"]/mods:titleInfo/mods:title', namespaces=nsmap):
      for related_uri in mods.iterfind('mods:relatedItem[@displayLabel="Metacollection"]/mods:identifier[@type="uri"]', namespaces=nsmap):
         #related_resources.append(['item', related_uri.text])
         related_resources = related_uri.text
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
   properties_raw.append(['ucldc_schema:campusunit', 'https://registry.cdlib.org/api/v1/repository/16/'])

   # collection
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

   return properties_raw

if __name__ == "__main__":
   sys.exit(main())
