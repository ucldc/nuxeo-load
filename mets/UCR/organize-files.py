#!/usr/bin/python
import sys, os
import subprocess
import shutil

''' organize the image files so they're ready for loading into nuxeo '''

CONTENT = [
    '/apps/content/UCR/huber_mets', 
    '/apps/content/UCR/laaqua_merritt',
    '/apps/content/UCR/western_waters_merritt'
    ]

METS = [
    '/apps/content/dsc_mets/9c2e65e471a83a104c2720d21da95ec3', # Tomas Rivera
    '/apps/content/dsc_mets/5a7ca55e2a4b2ac5c61f4691bd641299', # Huber
    '/apps/content/dsc_mets/43bfea40ac8775b512acf633b698306d', # Charles Lee Papers
    '/apps/content/dsc_mets/8ba98e66c2ce3e99cd1263a66744eebe' # Lippincott
    ]

def main():

    ''' s3://org.cdlib.calher also has some content files '''

    content = {}
    for dir in CONTENT:
        for root, dirs, files in os.walk(dir): 
            for file in files:
                if file.startswith('ark%3A%2F28722%2F') and file.endswith('.zip'):
                    id = file.split('.zip')[0]
                    id = id.split('ark%3A%2F28722%2F')[1]
                    content[id] = os.path.join(dir, file)
                elif file.startswith('ark%3A%2F13030%2F') and file.endswith('zip'):
                    id = file.split('.zip')[0]
                    id = id.split('ark%3A%2F13030%2F')[1]
                    content[id] = os.path.join(dir, file)

    #print content

    for dir in METS:
        for root, dirs, files in os.walk(dir):
            for file in files:
                id = file.split('.')[0]
                if id not in content:
                    print 'Content missing: {}/{}'.format(dir, file)
                else:
                    get_content(id, content[id])

def get_content(id, path):
    print path
    output = subprocess.check_output(
        [
            "unzip", "-jo", path, "store/v001/full/producer/FID1.tiff", "-d", "/apps/content/UCR/tmp"
        ],
        stderr = subprocess.STDOUT
    )

    moveto = '/apps/content/UCR/extracted_images/{}.tiff'.format(id) 
    shutil.move('/apps/content/UCR/tmp/FID1.tiff', moveto)

         
if __name__ == "__main__":
    sys.exit(main())
