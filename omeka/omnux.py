#!/usr/bin/env python

import requests, json, math, sys
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
    url = ''.join([api_baseurl, 'items?collection=', str(collection_id), '&page=', str(i)])
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


def transform_omeka_to_ucldc(omeka_item_dict, collection_id, omnux_fieldmap_json_file, collection_json_file, corpnames=[]):
  """ transform dict of items metadata from omeka api into nuxeo-friendly format """
  properties = {}

  # GET COLLECTION-LEVEL METADATA 
  with open(collection_json_file) as cf:
    collection_mapping_data = json.load(cf)
  collection_properties = get_collection_properties(collection_mapping_data, collection_id)
  properties.update(collection_properties)

  # GET ITEM-LEVEL METADATA
  collection_type = get_collection_property(collection_mapping_data, collection_id, "type")
  with open(omnux_fieldmap_json_file) as omf:
    omnux_mapping_data = json.load(omf)
  item_properties = get_item_properties(omnux_mapping_data, omeka_item_dict, collection_id, collection_type)
  properties.update(item_properties)

  # assemble payload
  payload = {} 
  path = get_path(omeka_item_dict, collection_mapping_data, collection_id)
  payload['path'] = path 
  payload['properties'] = properties

  return payload


def get_item_properties(omnux_mapping_data, omeka_item_dict, collection_id, collection_type):
  """ extract item properties from omeka metadata """
  properties = {}
  # Extract metadata out of 'element_texts' object
  for key in omeka_item_dict:
    if key == 'element_texts':
      metadata = transform_element_texts(omnux_mapping_data, omeka_item_dict[key], collection_id, collection_type)
      properties.update(metadata)
  
  return properties


def get_collection_properties(collection_mapping_data, collection_id):
  """ get collection-level properties """
  properties = {}
  
  # Collection ID
  ucldc_collection_id = get_collection_property(collection_mapping_data, collection_id, "ucldc_id")
  ucldc_collection = ''.join(('https://registry.cdlib.org/api/v1/collection/', str(ucldc_collection_id), '/'))
  properties['ucldc_schema:collection'] = [ucldc_collection]
  # Campus unit
  campusunit = get_collection_property(collection_mapping_data, collection_id, "campusunit")
  campusunit = ''.join(('https://registry.cdlib.org/api/v1/repository/', str(campusunit), '/'))
  properties['ucldc_schema:campusunit'] = [campusunit]
  # Type
  collection_type = get_collection_property(collection_mapping_data, collection_id, "type")
  properties['ucldc_schema:type'] = collection_type # FIXME not taking locally
  # Rights Status
  properties['ucldc_schema:rightsstatus'] = 'Copyrighted'
  # Rights Statement
  properties['ucldc_schema:rightsstatement'] = 'Transmission or reproduction of materials protected by copyright beyond that allowed by fair use requires the written permission of the copyright owners. Works not in the public domain cannot be commercially exploited without permission of the copyright owner. Responsibility for any use rests exclusively with the user.'
  
  return properties


def get_collection_property(collection_mapping_data, collection_id, property_name):
  """ get collection type (image, text, etc) """
  return collection_mapping_data["collection"][str(collection_id)][property_name]


def get_path(omeka_item_dict, collection_mapping_data, collection_id):
  filename = get_item_filename(omeka_item_dict)
  basepath = get_collection_property(collection_mapping_data, collection_id, "path")
  path = ''.join([basepath, filename])
  return path


def get_item_filename(omeka_item_dict):
  """ Get filename for a given item. Assumes one file. """
  # FIXME limit of 35 (?) chars for filename in path for Nuxeo. Need to translate Omeka filename into rationalized filename that we used for Nuxeo.
  # FIXME need to allow for more than one filename, or how to figure out definitive file for object.
  filename = omeka_item_dict['filenames'][0]
  return filename


def transform_element_texts(mapping_data, element_texts_object, collection_id, collection_type, corpnames=[]):
  """ transform 'element_texts' omeka metadata """
  metadata = {}

  # FIXME. There has got to be a better way to do this?!
  repeatables = defaultdict(list)
  singles = defaultdict(list)
  for item in element_texts_object:
    text, element_set_name, element_name = get_element_text(item)
    nuxeo_fieldname = mapping_data["element_texts"]["element_set"][element_set_name][element_name]["name"]
    if nuxeo_fieldname != 'do_not_map':
      nuxeo_fieldtype = mapping_data["element_texts"]["element_set"][element_set_name][element_name]["type"]
      if nuxeo_fieldtype == 'repeatable':
        repeatables[nuxeo_fieldname].append(text)
      else:
        singles[nuxeo_fieldname].append(text)

  for key, value in repeatables.iteritems():
    formatted_item = get_formatted_value(key, value, 'repeatable', collection_type)
    metadata[key] = formatted_item
  for key, value in singles.iteritems():
    formatted_item = get_formatted_value(key, value, 'single', collection_type)
    metadata[key] = formatted_item

  return metadata



def get_formatted_value(nuxeo_fieldname, value_list, item_type, collection_type):
  """ format list of values for nuxeo """
  if item_type == 'repeatable':
    value = []
    for item in value_list:
      formatted = format_fieldvalue(nuxeo_fieldname, item, collection_type)
      value.append(formatted)
  else:
    value = ". ".join(value_list)

  return value


def format_fieldvalue(nuxeo_fieldname, text, collection_type):
  """ format a value """
  if nuxeo_fieldname == 'ucldc_schema:subjecttopic':
    value = {'headingtype': 'topic', 'heading': text} #FIXME headingtype isn't taking locally
  elif nuxeo_fieldname == 'ucldc_schema:contributor':
    value = {'name': text}
  elif nuxeo_fieldname == 'ucldc_schema:creator':
    if text in corpnames:
      nametype = 'corpname'
    else:
      nametype = 'persname'
    value = {'name': text, 'nametype': nametype}
  elif nuxeo_fieldname == 'ucldc_schema:rightsholder':
    value = {'name': text}
  elif nuxeo_fieldname == 'ucldc_schema:date':
    # FIXME datetype doesn't seem to be taking?
    if collection_type == 'text':
      value = {'date': text, 'datetype': 'issued'}
    elif collection_type == 'image':
      value = {'date': text, 'datetype': 'created'}
    else:
      value = {'date': text, 'datetype': 'created'}
      print "WARNING: unrecognized collection_type:", collection_type
  elif nuxeo_fieldname == 'ucldc_schema:formgenre':
    value = {'heading': text}
  elif nuxeo_fieldname == 'ucldc_schema:language':
    value = {'language': text}
  else:
    value = text

  return value


def get_element_text(element_text_object):
  """ get metadata for a given Omeka 'element_texts' object """
  text = element_text_object['text']
  element_set_name = element_text_object['element_set']['name']
  element_name = element_text_object['element']['name']
  return text, element_set_name, element_name


def update_nuxeo(item_dict):
  """ update nuxeo """
  nx.update_nuxeo_properties(item_dict, path=item_dict['path'])


if __name__ == '__main__':
  main()
