#!/usr/bin/python
import sys, os
import argparse
import subprocess

IMAGE_DIR = '/apps/content/UCR/rivera'
IMAGES = [
    'hb0199n7pr',
    'hb1m3nb2fq',
    'hb2f59n92n',
    'hb3j49p11p',
    'hb7q2nb672', # has 4 images
    'hb809nb76r'
    ]
TEXT_DIR = '/apps/content/rescue/ucr/digitalassets.lib.berkeley.edu/calcultures/ucr/text/'
METS_DIR = '/apps/content/dsc_mets/9c2e65e471a83a104c2720d21da95ec3'
NX_FOLDER = '/asset-library/UCOP/barbaratest/rivera3'

def main():

    # need to map name of content files to mets using https://s3-us-west-2.amazonaws.com/org.cdlib.calher/ARKS-to-FILES.txt
    # convert ARKS-to-FILES to a dict. look up filename in 4th column. get ark from 1st column. get mets file from filename match.
    mapfile = 'ARKS-to-FILES.txt'
    arkmap = {}
    with open(mapfile) as f:
        for line in f:
            cols = line.split()
            v = cols[3].split('/')[-1]
            k = cols[0].split('/')[-1]
            
            arkmap[k] = v 
 
    files = [files for root, dirs, files in os.walk(METS_DIR)][0]
    files = [file for file in files if file.endswith('.mets.xml')]
    print len(files)

    for file in files:

        # create a nuxeo doc with path of the mets file we'll use to load metadata
        nxpath = os.path.join(NX_FOLDER, file)
        arkid = file.split('.')[0]
        type = 'SampleCustomPicture' if arkid in IMAGES else 'CustomFile' 
        print 'mkdoc', nxpath
        subprocess.check_output(
            [
                'nx', 'mkdoc', '-t', type, nxpath 
            ]
        )

        if arkid in IMAGES:
            # load image file as main content file
            sourcefile = arkmap[arkid] 
            sourcefile = os.path.join(IMAGE_DIR, sourcefile)
            print 'upfile', nxpath, sourcefile 
            subprocess.check_output(
                [
                    'nx', 'upfile', '-doc', nxpath, sourcefile
                ]
            )  
        else:
            # load .sgm and .xml content files as auxiliary files
            xmlfile = arkmap[arkid]
            source = os.path.join(TEXT_DIR, xmlfile)
            print 'nx extrafile', source

            subprocess.check_output(
                [
                    'nx', 'extrafile', source, nxpath
                ]
            )

            base = os.path.splitext(xmlfile)[0]
            sgmfile = '{}.sgm'.format(base)
            source = os.path.join(TEXT_DIR, sgmfile)
            print 'nx extrafile', source 

            subprocess.check_output(
                [
                    'nx', 'extrafile', source, nxpath
                ]
            )

if __name__ == "__main__":
    sys.exit(main())
