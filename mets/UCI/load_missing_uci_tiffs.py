#!/usr/bin/python
import sys, os
import argparse
import subprocess
from lxml import etree

METS_BASE = '/apps/content/dsc_mets/'
METS_DIR = {
                'MS-SEA002': 'b4952b1f8e9082c5193c875fdc6c5865',
                'MS-SEA006': 'f85e4caca8b6bf4c2c3cb628ffcd444c'
            } 
MAPFILE = '/apps/registry/nuxeo-load/mets/UCI/missing_uci_tiffs.txt'
IMAGE_DIR = '/apps/content/rescue/uci/images'
NX_BASE = '/asset-library/UCOP/dsc_mets3/UCI'

def main():
    # iterate over file of nuxeo docs missing tiffs
    with open(MAPFILE) as f:
        for line in f:
            cols = line.split()
    
            # get path of mets file
            collection = cols[1].split('/')[-2]
            mets_dir = os.path.join(METS_BASE, METS_DIR[collection])
            metsfile = cols[1].split('/')[-1]
            metspath = os.path.join(mets_dir, metsfile)
            print metspath
             
            # parse corresponding mets.xml file and get name of tiff 
            tree = etree.parse(metspath)
            root = tree.getroot()

            # grab the tiff and load it into nuxeo
            tiffname = get_tiffname(root)
            sourcefile = os.path.join(IMAGE_DIR, tiffname)
            nxpath = os.path.join(NX_BASE, collection, metsfile)
            print 'upfile', nxpath, sourcefile
            subprocess.check_output(
                [
                    'nx', 'upfile', '-doc', nxpath, sourcefile, '-f'
                ]
            )

def get_tiffname(document):
    ''' extract the name of the tiff from the mets file ''' 
    nsmap = {'mets': 'http://www.loc.gov/METS/'}

    fileSec = document.find('mets:fileSec', namespaces=nsmap)
    for file in fileSec.iterfind('mets:fileGrp/mets:file[@ID="FID1"]/mets:FLocat', namespaces=nsmap):
        url = file.get("{http://www.w3.org/1999/xlink}href")
        return url.split('/')[-1]

if __name__ == "__main__":
    sys.exit(main())
