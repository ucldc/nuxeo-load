#!/usr/bin/env python

import requests
import json
import math
import sys
from pynux import utils

#############################################################################
#############################################################################
class OmekaNuxeoImport:

  def __init__(self):
    """ Constructor """
    self.apiUrl = 'https://digital.library.ucsf.edu/api/'
    self.perPage = 50 # not sure if I can look this up somewhere

#############################################################################
  def getOmekaMetadata(self):
    """ get metadata out of Omeka """
    metadata = []
    collectionFields = list()
    itemFields = list()
    collectionElementSets = list()
    collectionElements = list()
    elementSets = list()
    elements = list()
    collectionIds = self.getCollections()
    print 'collectionIds:', collectionIds

    for collectionId in collectionIds:
      # treat image collections differently than text collection?
      collection_metadata = self.getCollectionMetadata(collectionId)
      print '\nNumber of items in collection', str(collectionId), ':', collection_metadata["items"]["count"] 

      # get fieldnames for collection metadata
      for key in collection_metadata:
        if key not in collectionFields:
          collectionFields.append(key)
      
      # get element_set names
      for element_text in collection_metadata["element_texts"]:
        if element_text["element_set"]["name"] not in collectionElementSets:
          collectionElementSets.append(element_text["element_set"]["name"])
        collectionElementSetNamePair = element_text["element_set"]["name"] + ':' + element_text["element"]["name"] 
        if collectionElementSetNamePair not in collectionElements:
          collectionElements.append(collectionElementSetNamePair)

      # do we have any populated extended_resources?
      for er in collection_metadata["extended_resources"]:
        print 'we have an extended resource!'

      # get metadata for all items in this collection
      items_metadata = self.getItemMetadata(collectionId, collection_metadata["items"]["count"])
      print 'Number of items in items_metadata', collectionId, ':', len(items_metadata)

      # for each item, get filename info
      for item_meta in items_metadata:
        itemFilenames = self.getItemFilenames(item_meta) # FIXME
#        print 'itemFilenames:', itemFilenames
        item_meta.update({'filenames': itemFilenames}) 

      # get fieldnames for item metadata
      for item_meta in items_metadata:
        for key in item_meta:
          if key not in itemFields:
            itemFields.append(key)
        # get names of element_sets used
        for element_text in item_meta["element_texts"]:
          if element_text["element_set"]["name"] not in elementSets:
            elementSets.append(element_text["element_set"]["name"])
          # get info for elements used
          elementSetNamePair = element_text["element_set"]["name"] + ':' + element_text["element"]["name"]
          if elementSetNamePair not in elements:
            elements.append(elementSetNamePair)
      for er in item_meta["extended_resources"]:
        print 'we have an extended resource!'

    #compile dict_of_field_info 
    #self.printFieldInfo(dict_of_field_info)
    payload = self.omeka_to_nuxeo_dict(items_metadata)
    # return payload

#############################################################################
  def omeka_to_nuxeo_dict (self, omeka_dict):
    """ transform dict of metadata from omeka api into json-esque nuxeo-friendly dict """
    properties = {}
    for item in omeka_dict:
      print '\n'
      for key in item:
        #print '\n'
        #print key, item[key]    

        # get metadata out of 'element_texts' node
        #if key == 'element_texts':
          #print 'text:', item[key][0]['text']
          #print 'element name:', item[key][0]['element']['name']
          # if it's DC metadata, then get that
          #'dc:title'
          # we seem to have DC Title, Description, Publisher, Date, Contributor, Rights, Format
          # we also have 'Item Type Metadata: name', e.g. "Original Format"

        # Rights Status (hardcoded)
          #'ucldc_schema:rightsstatus': 'copyrighted',
          # DC Rights, e.g. "Regents of the University of California"

        # Physical Description
          #'ucldc_schema:physdesc': 'Photographic print',
          # DC Description, e.g. ""Black and White Photograph\r\nUniversity of California, San Francisco, School of Nursing\r\n1923\r\n""

        # Collection ID
          #'ucldc_schema:collection': ['https://registry.cdlib.org/api/v1/collection/19/'],
          # item['collection']['id'] --> translate this to UCLDC collection ID

        # Campus Unit ID
          #'ucldc_schema:campusunit': ['https://registry.cdlib.org/api/v1/repository/16/'],
          # need to find UCSF campusunit ID

        # Local Identifier (what's this and do we need it?)
          #'ucldc_schema:localidentifier': ['2'],
          # item['id'] (this is the Omeka item ID. Don't think we want this.

        # Type
          #'ucldc_schema:type': 'image', 
          # Dublin Core 'Type', e.g. 'still image'
          # Dublin Core 'Format', e.g. 'photograph'
          # Item Type Metadata 'Original Format', e.g. 'Black and White Photograph'

        # Subject Topic
          #'ucldc_schema:subjecttopic': [{'headingtype': 'topic', 'heading': 'Laguna Beach (Calif.) -- Photographs'}],
          # DC Description, e.g. "Black and White Photograph\r\nUniversity of California, San Francisco, School of Nursing\r\n1923\r\n"

        # Date
          #'ucldc_schema:date': [{'inclusivestart': '1919', 'date': '1919 - 1949', 'datetype': 'created', 'inclusiveend': '1949'}],
          # DC Date, e.g. "1923"

        # Rights Statement
          #'ucldc_schema:rightsstatement': 'This material is provided for private study, scholarship, or research. Transmission or reproduction of any material protected by copyright beyond that allowed by fair use requires the written permission of the copyright owners. The creators of the material or their heirs may retain copyright to this material.', 

        # Place
          #'ucldc_schema:place': [{'name': 'Laguna Beach (Calif.)'}], 

        # Creator
          #'ucldc_schema:creator': [{'nametype': 'persname', 'role': 'Photographer', 'name': 'Cochems, Edward W. (Edward William), 1874-1949'}], 

        # Physical Location
          #'ucldc_schema:physlocation': 'Box 1 : Folder 1'
      
#############################################################################
  def printFieldInfo(self, dict_of_field_info):
    """ Print information on the metadata fields we have  """
    # FIXME - this doesn't work yet.
    print '\n# collectionFields #'
    for field in collectionFields:
      print field

    print '\n# itemFields #'
    for field in itemFields:
      print field

    print '\n# collectionElementSets #'
    for set in collectionElementSets:
      print set

    print '\n# collectionElements #'
    for element in collectionElements:
      print element

    print '\n# elementSets #'
    for set in elementSets:
      print set 

    print '\n# elements #'
    for element in elements:
      print element
 
    # return metadata in one big dict. or just load collection right into Nuxeo?
    print collection_metadata
    print items_metadata

#############################################################################
  def getItemFilenames(self, metadata):
    """ get filename(s) for a given item """
    filenames = []
    # get api url for files
    url = metadata["files"]["url"]
    metadata = self.callOmekaApi(url)
    for file_meta in metadata:
      filenames.append(file_meta["filename"])

    return filenames

#############################################################################
  def callOmekaApi(self, url):
    """ call UCSF Omeka API """
    #print '\nurl:', url
    r = requests.get(url)
    #print 'status_code was:', r.status_code, 'content-type was:', r.headers['content-type']
    #print type(r.json())
    return r.json() 

#############################################################################
  def getItemMetadata(self, collectionId, itemCount):
    """ get metadata for items in a given collection from Omeka """
    metadata = list() 
    pageCount = int(math.ceil(itemCount/float(self.perPage)))
    print 'pageCount:', pageCount
    i = 1 
    while i <= pageCount: 
      url = self.apiUrl + 'items?collection=' + str(collectionId) + '&page=' + str(i)
      i = i + 1
      #print 'url:', url
      pageMetadata = self.callOmekaApi(url) # returns a list of dicts
      #print 'pageMetadata len:', len(pageMetadata)
      #print 'pageMetadata type:', type(pageMetadata)
      for item in pageMetadata: # each item is a dict with 13 elements
        #print 'item type:', type(item)
        #print 'item len:', len(item)
        metadata.append(item)
    return metadata
    #print '\nurl:', url
    #r = requests.get(url)
    #print 'status_code was:', r.status_code, 'content-type was:', r.headers['content-type']
    #return r.json()

#############################################################################
  def getElementCount(self, elementSetId):
    """ get element count for a given element_set """
    url = self.apiUrl + 'element_sets/' + str(elementSetId)
    return self.callOmekaApi(url)
 
#############################################################################
  def getElementNames(self, elementSetId, elementCount):
     """ get element names for a given element_set """
     print 'elementSetId:', elementSetId
     print 'elementCount:', elementCount
     # should deal with paging here but I know there are fewer than 50 so I'm being lazy
     url = self.apiUrl + 'elements?element_set=' + str(elementSetId)
     element_metadata = self.callOmekaApi(url)
     for element in element_metadata:
       print element["name"]

#############################################################################
  def getCollectionMetadata(self, collectionId):
    """ get metadata for a given collection from Omeka """
    #print '\ncollectionId: ', collectionId
    url = self.apiUrl + 'collections/' + str(collectionId)
    #r = requests.get('https://digital.library.ucsf.edu/api/collections/' + str(collectionId)) 
    #print 'status_code was:', r.status_code, 'content-type was:', r.headers['content-type']
    return self.callOmekaApi(url)  

#############################################################################
  def getCollections(self):
    """ get collection IDs """
    # not sure if we'll have a list of names or what.
    #1) A History of UCSF. id = 10.
    #2) 30th General Hospital. id = 13. 10 items total
    #3) Photograph Collection. id = 6.
    #4) School of Dentistry 130th Anniversary. id = 9.
    #5) Robert L. Day Digital Image Collection. id = 14.
    #6) The Reinhard S. Speck Cholera Collection. id = 8.
    #collectionIds = [10, 13, 6, 9, 14, 8]
    collectionIds = [13]
    return collectionIds 
    
#############################################################################
def runImport():
  """ import content from Omeka instance into Nuxeo """
  omekaNuxeoImport = OmekaNuxeoImport()
  payload = omekaNuxeoImport.getOmekaMetadata() 
  #omekaNuxeoImport.loadBatchIntoNuxeo(payload)
  
#############################################################################
if __name__ == '__main__':
  print "\n### omekaUcldcImport.py ###\n"
  runImport()
  print "\n### Done! ###\n"
