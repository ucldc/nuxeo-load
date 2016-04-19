#!/usr/bin/env python

import requests, json, math, sys, os
from pynux import utils
from collections import defaultdict

per_page = 50 # not sure if I can look this up somewhere

def main():
  pass
  # try getting args. Figure out usage.


def call_omeka_api(url):
  """ call Omeka API """
  r = requests.get(url)
  return r.json()


def extract_collection(api_baseurl, collection_id):
  """ get metadata for a given collection from Omeka """
  url = api_baseurl + 'collections/' + str(collection_id)
  return call_omeka_api(url)


def get_item_count(api_baseurl, collection_id):
  """ get item count for a collection """
  # Omeka-Total-Results header
  if collection_id == 0:
      url = api_baseurl + 'items'
      r = requests.get(url)
      count = int(r.headers['Omeka-Total-Results'])
  else:
      collection_metadata = extract_collection(api_baseurl, collection_id)
      count = collection_metadata["items"]["count"]

  return count


def extract_items(api_baseurl, collection_id):
  """ get metadata for items in a given collection from Omeka """
  metadata = []
  item_count = get_item_count(api_baseurl, collection_id)
  page_count = int(math.ceil(item_count/float(per_page)))
  i = 1
  while i <= page_count:
    url = "{}items?page={}".format(api_baseurl, i)
    if collection_id:
        url = "{}&collection={}".format(url, collection_id)
    i = i + 1
    page_metadata = call_omeka_api(url) # returns a list of dicts
    for item in page_metadata: # each item is a dict with 13 elements
      # append filenames to item
      filenames = [] 
      files_url = item["files"]["url"]
      files_metadata = call_omeka_api(files_url)
      for fm in files_metadata:
        filenames.append(fm["filename"])
      item.update({'filenames': filenames})
      metadata.append(item)
  return metadata


def extract_single_item(api_baseurl, item_id):
    """ get metadata for an omeka item """
    url = "{}items/{}".format(api_baseurl, item_id)
    metadata = call_omeka_api(url)
    filenames = get_item_filenames(api_baseurl, item_id)
    metadata['filenames'] = filenames
  
    return metadata

def get_item_filenames(api_baseurl, omeka_item_id):
    ''' get filenames associated with given Omeka item id '''
    filenames = []

    url = "{}files?item={}".format(api_baseurl, omeka_item_id)    
    files_metadata = call_omeka_api(url)
    for fm in files_metadata:
        filenames.append(fm["filename"])
    
    return filenames

def transform_omeka_to_ucldc(omeka_item_dict, collection_id, omnux_fieldmap_json_file, collection_json_file, hardlinks={}, corpnames=[]):
  """ transform dict of items metadata from omeka api into nuxeo-friendly format """
  properties_raw = []

  # GET COLLECTION-LEVEL METADATA
  with open(collection_json_file) as cf:
    collection_mapping_data = json.load(cf)
  collection_properties = get_collection_properties(collection_mapping_data, collection_id)
  properties_raw.extend(collection_properties)
  
  
  # GET ITEM-LEVEL METADATA
  collection_type = get_collection_property(collection_mapping_data, collection_id, "type")
  with open(omnux_fieldmap_json_file) as omf:
    omnux_mapping_data = json.load(omf)
  item_properties = get_item_properties(omnux_mapping_data, omeka_item_dict, collection_id, collection_type, corpnames)
  properties_raw.extend(item_properties)

  # AGGREGATE AND FORMAT METADATA
  properties = format_properties(properties_raw, collection_type, corpnames)

  # ASSEMBLE PAYLOAD
  payload = {}
  path = get_path(omeka_item_dict, collection_mapping_data, collection_id, hardlinks)
  payload['path'] = path
  payload['properties'] = properties

  return payload


def get_item_properties(omnux_mapping_data, omeka_item_dict, collection_id, collection_type, corpnames=[]):
  """ extract item properties from omeka metadata """
  properties = [] 

  for key in omeka_item_dict:
    if key == 'element_texts':
      element_text_properties = transform_element_texts(omnux_mapping_data, omeka_item_dict[key])
      properties.extend(element_text_properties)
    elif key == 'tags':
      tag_properties = transform_tags(omnux_mapping_data, omeka_item_dict[key])
      properties.extend(tag_properties)

  return properties


def get_collection_properties(collection_mapping_data, collection_id):
  """ get collection-level properties """
  properties = [] 

  # Collection ID
  ucldc_collection_id = get_collection_property(collection_mapping_data, collection_id, "ucldc_id")
  ucldc_collection = ''.join(('https://registry.cdlib.org/api/v1/collection/', str(ucldc_collection_id), '/'))
  properties.append([u'ucldc_schema:collection', ucldc_collection])
  # Campus unit
  campusunit = get_collection_property(collection_mapping_data, collection_id, "campusunit")
  campusunit = ''.join(('https://registry.cdlib.org/api/v1/repository/', str(campusunit), '/'))
  properties.append([u'ucldc_schema:campusunit', campusunit])
  # Type
  collection_type = get_collection_property(collection_mapping_data, collection_id, "type")
  properties.append([u'ucldc_schema:type', collection_type])
  # Rights Status
  properties.append([u'ucldc_schema:rightsstatus', 'Copyrighted'])
  # Rights Statement
  properties.append([u'ucldc_schema:rightsstatement', 'Transmission or reproduction of materials protected by copyright beyond that allowed by fair use requires the written permission of the copyright owners. Works not in the public domain cannot be commercially exploited without permission of the copyright owner. Responsibility for any use rests exclusively with the user.'])

  return properties


def get_collection_property(collection_mapping_data, collection_id, property_name):
  """ get collection type (image, text, etc) """
  return collection_mapping_data["collection"][str(collection_id)][property_name]


def get_path(omeka_item_dict, collection_mapping_data, collection_id, hardlinks={}):
  filename = get_item_filename(omeka_item_dict, hardlinks)
  basepath = get_collection_property(collection_mapping_data, collection_id, "nuxeo_folder")
  collection_name = get_collection_property(collection_mapping_data, collection_id, "name")
  path = os.path.join(basepath, collection_name, filename)
  return path


def get_item_filename(omeka_item_dict, hardlinks={}):
  """ Get filename for a given item. Assumes one file. """
  # FIXME need to allow for more than one filename, or how to figure out definitive file for object.
  filename = omeka_item_dict['filenames'][0]
  if filename in hardlinks:
    filename = hardlinks[filename]

  return filename


def transform_element_texts(mapping_data, element_texts_object):
  """ transform 'element_texts' omeka metadata """
  metadata = []

  for item in element_texts_object:
    text, element_set_name, element_name = get_element_text(item)
    nuxeo_fieldname = mapping_data["element_texts"]["element_set"][element_set_name][element_name]["name"]
    if nuxeo_fieldname != 'do_not_map':
      metadata.append([nuxeo_fieldname, text])
 
  return metadata


def transform_tags(mapping_data, tags_object):
  metadata = [] 
  nuxeo_fieldname = mapping_data["tags"]["name"]
  if nuxeo_fieldname != 'do_not_map':
    for item in tags_object: 
      metadata.append([nuxeo_fieldname, item["name"]])

  return metadata


def format_properties(properties_list, collection_type, corpnames=[]):
  """ Take a list of [name, value] lists and return a dict of formatted values per property """
  properties = {}

  # get list of unique property names
  property_names = [p[0] for p in properties_list]
  property_names_set = set(property_names)
  property_names_unique = list(property_names_set)

  # aggregate and format values for each property name
  for name in property_names_unique:
    property_values = []
    formatted_property = {}
    for sublist in properties_list:
      if sublist[0] == name:
        property_values.append(sublist[1])
    formatted_value = get_formatted_value(name, property_values, collection_type, corpnames)
    formatted_property[name] = formatted_value
    properties.update(formatted_property)

  return properties


def get_formatted_value(nuxeo_fieldname, value_list, collection_type="", corpnames=[]):
  """ format list of values for nuxeo """
  repeatables = ("ucldc_schema:collection", "ucldc_schema:campusunit", "ucldc_schema:description", "ucldc_schema:subjecttopic", "ucldc_schema:contributor", "ucldc_schema:creator", "ucldc_schema:date", "ucldc_schema:formgenre", "ucldc_schema:localidentifier", "ucldc_schema:language", "ucldc_schema:publisher", "ucldc_schema:relatedresource", "ucldc_schema:rightsholder")

  # format values
  if nuxeo_fieldname in repeatables:
    value = []
    for item in value_list:
      formatted = format_fieldvalue(nuxeo_fieldname, item, collection_type, corpnames)
      value.append(formatted)
  else:
    value = ". ".join(value_list)

  return value


def format_fieldvalue(nuxeo_fieldname, text, collection_type="", corpnames=[]):
  """ format a value """
  if nuxeo_fieldname == 'ucldc_schema:subjecttopic':
    value = {'headingtype': 'topic', 'heading': text}
  elif nuxeo_fieldname == 'ucldc_schema:creator' or nuxeo_fieldname == 'ucldc_schema:contributor':
    if text.strip() in corpnames:
      nametype = 'corpname'
    else:
      nametype = 'persname'
    value = {'name': text, 'nametype': nametype}
  elif nuxeo_fieldname == 'ucldc_schema:rightsholder':
    value = {'name': text}
  elif nuxeo_fieldname == 'ucldc_schema:date':
    if collection_type == 'text':
      value = {'date': text, 'datetype': 'issued'}
    elif collection_type == 'image':
      value = {'date': text, 'datetype': 'created'}
    else:
      value = {'date': text, 'datetype': 'created'}
      print "WARNING: unrecognized collection_type:", collection_type
  elif nuxeo_fieldname == 'ucldc_schema:description':
    value = {'item': text, 'type': 'scopecontent'}
  elif nuxeo_fieldname == 'ucldc_schema:formgenre':
    value = {'heading': text}
  elif nuxeo_fieldname == 'ucldc_schema:language':
    text = text.strip()
    code = ''
    if text == 'English':
      code = 'eng'
    elif text == 'Dutch':
      code = 'dut'
    elif text == 'French':
      code = 'fre'
    elif text == 'German':
      code = 'ger'
    elif text == 'Spanish':
      code = 'spa'
    value = {'language': text, 'languagecode': code}
  else:
    value = text

  return value


def get_element_text(element_text_object):
  """ get metadata for a given Omeka 'element_texts' object """
  text = element_text_object['text']
  element_set_name = element_text_object['element_set']['name']
  element_name = element_text_object['element']['name']
  return text, element_set_name, element_name


if __name__ == '__main__':
  main()
