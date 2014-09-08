#!/usr/bin/env python
#coding=utf-8
""" grab mets files from UCB server """
import urllib2

def main():
    with open("mets_index.html", "r") as f:
        for line in f:
            if line.find("xml") == 69:
                filename = line[74:94]
                print "filename:", filename
                grabfile(filename)

def grabfile(filename):
    url = "http://digitalassets.lib.berkeley.edu/jpnprints/ucsf/mets/" + filename
    dest = "/apps/content/metadata/UCSF/jpn-woodblocks/ucb/" + filename
    print url
    response = urllib2.urlopen(url)
    xml = response.read()
    with open(dest, "wb") as mets:
        mets.write(xml)

if __name__ == '__main__':
    main()
