#!/usr/bin/env python

import requests
import json
import math

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
      for key in collection_metadata:
        if key not in collectionFields:
          collectionFields.append(key)
      
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
        #itemFilenames = self.getItemFilenames(item_meta) # FIXME
        #print 'itemFilenames:', itemFilenames
        # get item field names
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
  omekaNuxeoImport.getOmekaMetadata() 
  #omekaNuxeoImport.loadBatchIntoNuxeo()
  
#############################################################################
if __name__ == '__main__':
  print "\n### omekaUcldcImport.py ###\n"
  runImport()
  print "\n### Done! ###\n"
