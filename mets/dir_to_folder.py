#!/usr/bin/python
import sys, os
import argparse
import subprocess

def main(local_dir, nx_folder, pynuxrc):
    files = [files for root, dirs, files in os.walk(local_dir)][0]

    for file in files:
        filepath = os.path.join(local_dir, file)
        print filepath 
       
        subprocess.check_output(
            [
                'nx', 'upfile', '-dir', nx_folder, filepath 
            ]
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='load contents of a local dir into a nuxeo folder')
    parser.add_argument('local_dir', help='local directory containing files to upload')
    parser.add_argument('nx_folder', help='path to nuxeo folder')
    parser.add_argument(
        '--pynuxrc', default='~/.pynuxrc', help='rc file for use by nxcli')

    argv = parser.parse_args()

    local_dir = argv.local_dir
    nxpath = argv.nx_folder
    pynuxrc = argv.pynuxrc

    sys.exit(
        main(
             local_dir, nxpath, pynuxrc))
